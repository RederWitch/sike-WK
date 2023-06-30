import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd, messagebox, Scrollbar, Text
from threading import Thread
import argparse
import socket
import sys
import threading
import hashlib
from Crypto.Cipher import AES

import sike as sike

BUFFER_SIZE = 1024
ENCODING = 'utf-16'

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
NEW_LINE = '\n'
PRE_TEXT = NEW_LINE + CURSOR_UP_ONE + ERASE_LINE
EXCHANGE_CONFIRMATION = b'***CONFIRMED_EXCHANGE****'


def frame_changer(frame_name):
    frame_name.tkraise()


def chat_bubble(sender, text: str, text_view):
    text_place = '1.0'
    text_view.config(state='normal')
    text_view.insert(text_place, "\n>" + text)
    if sender == "me":
        text_view.insert(text_place, "\n\n\tME -->")
    elif sender == "info":
        text_view.insert(text_place, "\n\n\tINFO-->")
    else:
        text_view.insert(text_place, "\n\n\tBOB-->")

    text_view.config(state='disabled')

class GlobalData():
    work_mode = None

    ip_add_input = None
    thread = None

    text_view = None
    socket = None


class App(tk.Tk):
    global_data = GlobalData()
    def __init__(self):
        super().__init__()
        self.title('Communicator')

        # Style -> looks of widgets
        self.style = ttk.Style(self)
        self.style.configure('TFrame', background='white')
        self.style.configure('TLabel', background='white')
        self.style.configure(
            'TButton',
            border=2,
            relief='SOLID',
            foreground='white',
            # font=('Roboto', 14),
            background='#5D72E5'

        )
        self.style.configure('FI.TButton', background="white")

        self.style.map('TButton',
                       background=[('active', '#3F51B5')]
                       )
        self.style.map('FI.TButton',
                       background=[('active', '#BDBDBD')]
                       )
        self.style.configure('TRadiobutton', background='white', font=("Roboto", 18, 'bold'), indicator=0)

        # configure the root window
        window_width = 1200
        window_height = 800

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.config(bg='#EDEDED')

        # prevent from resizing
        self.resizable(True, True)

        # icon
        icon = tk.PhotoImage(file="./assets/sike_icon.png")
        self.wm_iconphoto(False, icon)

        # Always visible header
        header_frame = ttk.Frame(self, height=70, width=1200)
        header_frame['style'] = 'TFrame'
        header_frame.pack(fill='x', ipady=18)

        header_title = ttk.Label(header_frame, text='Communicator', style='TLabel')
        header_title.configure(font=("Roboto", 36))
        header_title.pack(side='left', padx=10, fill='x')

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartFrame, ConnectFrame, ChatFrame):
            frame = F(container, self, self.global_data)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.pack(
                ipadx=500,
                padx=350,
                pady=105
            )

        self.frames[StartFrame].tkraise()

        # to display the current frame passed as
        # parameter

    def show_frame(self, present, cont):
        self.frames[present].forget()
        frame = self.frames[cont]
        frame.tkraise()
        frame.pack(
            ipadx=500,
            padx=350,
            pady=105
        )

    def on_close(self):
        if self.global_data.socket:
            self.global_data.socket.socket.close()
        self.destroy()
        sys.exit()


class PanelFrame(ttk.Frame):
    def __init__(self, container, controller, title: str):
        super().__init__(container, style='TFrame')
        self.controller = controller
        label = ttk.Label(self, text=title, style='TLabel')
        label.configure(font=("Roboto", 24, 'bold'))
        label.pack(side="top", fill="x", pady=20, padx=40)

    def create_button(self, container, button_label: str):
        button = ttk.Button(container, text=button_label, style='TButton')
        return button

    def create_text_input(self, container, input_label: str, input_holder: tk.StringVar, return_entry=False):
        input_frame = ttk.Frame(container, style='TFrame')
        ttk.Label(input_frame, text=input_label).pack(fill='x', expand=True, pady=3)
        entry = ttk.Entry(input_frame,
                  textvariable=input_holder,
                  width=26,
                  style='TEntry',
                  font=('Roboto', 14)
                  )
        entry.pack(fill='x', expand=True)
        if return_entry:
            return input_frame, entry
        else:
            return input_frame


class StartFrame(PanelFrame):
    def __init__(self, container, controller, global_data):
        super().__init__(container, controller, 'Chose mode')
        self.selected_mode = tk.StringVar()
        self.global_data = global_data

        s = ttk.Radiobutton(
            self,
            text='SERVER',
            value='server',
            variable=self.selected_mode
        )
        s.pack(side="top", fill="x", pady=45, padx=85)
        r = ttk.Radiobutton(
            self,
            text='CLIENT',
            value='client',
            variable=self.selected_mode
        )
        r.pack(side="top", fill="x", pady=45, padx=85)

        button_start = self.create_button(self, 'START')
        button_start.configure(command=self.star_button_action)
        button_start.pack(side="top", fill="x", pady=45, padx=190, )

    def star_button_action(self):
        work_mode = self.selected_mode.get()
        self.global_data.work_mode = work_mode
        if work_mode == 'server':
            self.global_data.ip_add_input.config(state='disable')
        if work_mode:
            self.controller.show_frame(StartFrame, ConnectFrame)



class ConnectFrame(PanelFrame):
    def __init__(self, container, controller, global_data):
        super().__init__(container, controller, 'Enter data')
        self.global_data = global_data
        self.addr_ip = tk.StringVar()
        self.port = tk.StringVar()
        self.key_path = tk.StringVar()
        self.select_file_img = tk.PhotoImage(file='./assets/icons8-share-rounded-90.png').subsample(3, 3)
        ip_addr_input, self.global_data.ip_add_input = self.create_text_input(self, "Address IP", self.addr_ip, return_entry=True)
        ip_addr_input.pack(side="top", fill="x", pady=5, padx=85)
        self.create_text_input(self, "Port", self.port).pack(side="top", fill="x", pady=5, padx=85)

        self.create_file_input().pack(side="top", fill="x", pady=3, padx=85)

        button_start = self.create_button(self, 'CONNECT')
        button_start.configure(command=self.star_button_action)

        button_start.pack(side="top", fill="x", pady=45, padx=190)

    def select_file(self, label):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        label.configure(text=filename)
        self.key_path = filename

    def create_file_input(self):
        self.key_path = None
        input_frame = ttk.Frame(self, style='TFrame')

        label_file_name = ttk.Label(input_frame, text="Chose file with KEY")
        if_button = ttk.Button(
            input_frame,
            image=self.select_file_img,
            command=lambda: self.select_file(label_file_name),
            style="FI.TButton"
        )
        if_button.pack(side='left')
        label_file_name.pack(side='left', padx=5)
        return input_frame

    def star_button_action(self):
        # TODO zedytować niepotrzebne globalne
        addr_ip = self.addr_ip.get()
        port_connect = None
        if len(self.port.get()) != 0:
            port_connect = self.port.get()
        external_key = self.key_path

        if addr_ip is not None and external_key is not None:
            if self.global_data.work_mode == "client":
                if not port_connect:
                    return
            self.global_data.thread = Thread(target=try_connect, args=(self.global_data.work_mode, external_key, port_connect, self.global_data, addr_ip,))
            self.global_data.thread.daemon = True
            self.global_data.thread.start()
            self.controller.show_frame(ConnectFrame, ChatFrame)


class ChatFrame(PanelFrame):
    def __init__(self, container, controller, global_data):
        super().__init__(container, controller, 'ChatRoom')
        self.global_data = global_data
        # noinspection PyStatementEffect
        self.msg_to_send = tk.StringVar()
        self.select_file_img = tk.PhotoImage(file='./assets/icons8-send-96.png').subsample(3, 3)

        all_frame = ttk.Frame(self)
        all_frame.pack(side="top", fill="x", pady=3, padx=85)

        chat_frame = ttk.Frame(all_frame, style='TFrame', borderwidth=1, relief='sunken', height=300)
        chat_frame.pack(side="top", fill="both", expand=True)
        chat_frame.pack_propagate(False)

        scrollbar = tk.Scrollbar(chat_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        text_box = tk.Text(
            chat_frame,
            state='disabled',
            width=40,
            height=20,
            wrap='word',
            relief='flat'
        )
        text_box.pack(fill="both", expand=True)
        scrollbar.configure()

        text_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_box.yview)
        self.global_data.text_view = text_box

        input_send_frame = ttk.Frame(all_frame, style='TFrame')
        input_send_frame.pack(side="bottom", fill="x", expand=True)
        ttk.Entry(input_send_frame,
                  textvariable=self.msg_to_send,
                  # width=26,
                  style='TEntry',
                  font=('Roboto', 14)
                  ).pack(fill='x', expand=True, side="left")
        send_button = ttk.Button(
            input_send_frame,
            image=self.select_file_img,
            command=self.send_button_action,
            style="FI.TButton"
        )
        send_button.pack(side="right")

    def send_button_action(self):
        text = self.msg_to_send.get()
        self.msg_to_send.set("")
        chat_bubble("me", text, self.global_data.text_view)
        self.global_data.socket.send_msg(text)


def server_side(server_port, external_key, global_data):
    server_socket = Server(global_data.text_view, secure=True)
    global_data.socket = server_socket
    try:
        server_socket.start(external_key=external_key, port=server_port)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        server_socket.socket.close()
        chat_bubble('info', 'Connection closed', global_data.text_view)


def client_side(destination, port, external_key, global_data):
    client_socket = Client(global_data.text_view, secure=True)
    global_data.socket = client_socket
    try:
        client_socket.connect(destination, port, external_key)
    except (Exception, KeyboardInterrupt) as e:
        client_socket.socket.close()
        chat_bubble('info', 'Connection closed', global_data.text_view)
        raise


def try_connect(mode: str, key_file, port, global_data, address=None):
    if not port:
        port = 8888
    if mode == "server":
        server_side(int(port), key_file, global_data)
    elif mode == "client":
        if port and address:
            client_side(address, int(port), key_file, global_data)
        else:
            raise Exception()
    else:
        print("Error")

def padding(s):
    return s + (((8 - len(s) % 8) - 1) * '~')


def remove_padding(s: str):
    return s.replace('~', '')


def load_auth_key(external_key):
    sha256 = hashlib.sha256()
    with open(external_key, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def save_auth_key(new_auth_key, external_key):
    f = open(external_key, "wb")
    f.write(new_auth_key)
    f.close()


class SendMessageBase:
    def _send_message(self, socket, text, ):
        if not self.aes:
            self.aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])
        raw_data = text
        if raw_data:
            if self.is_secure:

                data = padding(raw_data).encode(ENCODING)
                encrypted_data = self.aes.encrypt(data)
                socket.send(bytes(encrypted_data))
            else:
                socket.send(bytes(raw_data, ENCODING))


class Server(SendMessageBase):
    def __init__(self,
                 chat_text_box,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True
                 ):
        self.chat_text_box = chat_text_box
        self.socket = socket.socket(socket_family, socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = None
        self.key = 'Sixteen byte key'
        self.aes = None
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        chat_bubble('info', 'Exchanging key...', self.chat_text_box)
        public_key = self.connection.recv(BUFFER_SIZE)
        chat_bubble('info', 'Encapsulating key...', self.chat_text_box)
        shared_secret, ciphertext = self.sike_api.encapsulate(public_key)
        chat_bubble('info', 'Sending cypher text message...', self.chat_text_box)
        self.connection.sendall(ciphertext)
        chat_bubble('info', 'Waiting for confirmation...', self.chat_text_box)
        confirmation = self.connection.recv(BUFFER_SIZE)
        if not confirmation == EXCHANGE_CONFIRMATION:
            self.socket.close()
        chat_bubble('info', 'Key exchanged.', self.chat_text_box)
        return shared_secret

    def send_msg(self, text):
        self._send_message(self.connection, text)

    def start(self, external_key, port):
        self.socket.bind(('', port))
        chat_bubble('info', 'Listening on port ' + str(port) + '...', self.chat_text_box)
        self.socket.listen()
        try:
            self.connection, addr = self.socket.accept()
        except KeyboardInterrupt:
            self.socket.close()
            chat_bubble('info', 'Connection closed', self.chat_text_box)
            sys.exit(1)

        with self.connection:
            chat_bubble('info', 'Connected by ' + str(addr[0]), self.chat_text_box)
            chat_bubble('info', 'Authorization in progress...', self.chat_text_box)
            server_auth_key = load_auth_key(external_key)
            client_auth_key = str(self.connection.recv(BUFFER_SIZE), ENCODING)
            if server_auth_key != client_auth_key:
                chat_bubble('info', 'Authorization failed', self.chat_text_box)
                exit(-1)
            else:
                chat_bubble('info', 'Authorization successful', self.chat_text_box)
                self.connection.send(bytes('200', ENCODING))

            aes = None
            if self.is_secure:
                self.key = self.key_exchange()
                save_auth_key(self.key, external_key)
                chat_bubble('info', "Key saved", self.chat_text_box)
                aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])
            try:
                while True:
                    raw_data = self.connection.recv(BUFFER_SIZE)
                    if self.is_secure:
                        decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                        chat_bubble("2", decrypted_data, self.chat_text_box)
                    else:
                        chat_bubble('2', str(raw_data), self.chat_text_box)
                    if not raw_data:
                        break
            except KeyboardInterrupt:
                pass
        self.socket.close()
        chat_bubble('info', 'Connection closed', self.chat_text_box)


class Client(SendMessageBase):

    def __init__(self,
                 chat_text_box,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True,
                 ):
        self.chat_text_box = chat_text_box
        self.socket = socket.socket(socket_family, socket_type)
        self.key = 'Sixteen byte key'
        self.aes = None
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        chat_bubble('info', 'Exchanging key', self.chat_text_box)
        public_key, secret_key = self.sike_api.generate_key()
        self.socket.send(public_key)

        cyphertext_message = self.socket.recv(BUFFER_SIZE)
        chat_bubble('info', 'Decapsulating shared key...', self.chat_text_box)
        shared_secret = self.sike_api.decapsulate(secret_key, cyphertext_message)
        self.socket.send(EXCHANGE_CONFIRMATION)
        chat_bubble('info', 'Key exchanged.', self.chat_text_box)
        return shared_secret

    def send_msg(self, text):
        self._send_message(self.socket, text)

    def connect(self, destination, port, external_key):
        aes = None
        self.socket.connect((destination, port))
        chat_bubble('info', 'Connected with server', self.chat_text_box)
        chat_bubble('info', 'Authorization in progress...', self.chat_text_box)
        auth_key = load_auth_key(external_key)
        self.socket.send(bytes(auth_key, ENCODING))
        if str(self.socket.recv(BUFFER_SIZE), ENCODING) != "200":
            chat_bubble('info', 'Authorization failed', self.chat_text_box)
            exit(-1)
        else:
            chat_bubble('info', 'Authorization successful', self.chat_text_box)

        if self.is_secure:
            self.key = self.key_exchange()
            save_auth_key(self.key, external_key)
            chat_bubble('info', "Key saved", self.chat_text_box)
            aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])

        try:
            while True:
                raw_data = self.socket.recv(BUFFER_SIZE)
                if not raw_data:
                    break
                if self.is_secure:
                    decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                    chat_bubble("2", decrypted_data, self.chat_text_box)
                else:
                    chat_bubble('2', str(raw_data), self.chat_text_box)
        except KeyboardInterrupt:
            pass

        self.socket.close()
        chat_bubble('info', 'Connection closed', self.chat_text_box)
