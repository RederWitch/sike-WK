import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd, messagebox, Scrollbar, Text
from threading import Thread
import argparse
import logging
import socket
import sys
import threading
import hashlib
from Crypto.Cipher import AES

import sike as sike

WORK_MODE = None

ADDR_IP = None
PORT = None
KEY_PATH = None

TEXT_VIEW = None
SOCET=None

def frame_changer(frame_name):
    frame_name.tkraise()


def chat_bubble(sender, text: str):
    text_place = '1.0'
    global TEXT_VIEW
    TEXT_VIEW.config(state='normal')
    TEXT_VIEW.insert(text_place, "\n>" + text)
    if sender == "me":
        TEXT_VIEW.insert(text_place, "\n\n\tME -->")
    elif sender == "info":
        TEXT_VIEW.insert(text_place, "\n\n\tINFO-->")
    else:
        TEXT_VIEW.insert(text_place, "\n\n\tBOB-->")

    TEXT_VIEW.config(state='disabled')


class App(tk.Tk):
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
            frame = F(container, self)

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

    def create_text_input(self, container, input_label: str, input_holder: tk.StringVar):
        input_frame = ttk.Frame(container, style='TFrame')
        ttk.Label(input_frame, text=input_label).pack(fill='x', expand=True, pady=3)
        ttk.Entry(input_frame,
                  textvariable=input_holder,
                  width=26,
                  style='TEntry',
                  font=('Roboto', 14)
                  ).pack(fill='x', expand=True)
        return input_frame


class StartFrame(PanelFrame):
    def __init__(self, container, controller):
        super().__init__(container, controller, 'Chose mode')
        self.selected_mode = tk.StringVar()

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
        global WORK_MODE
        WORK_MODE = self.selected_mode.get()
        self.controller.show_frame(StartFrame, ConnectFrame)


class ConnectFrame(PanelFrame):
    def __init__(self, container, controller):
        super().__init__(container, controller, 'Enter data')
        self.addr_ip = tk.StringVar()
        self.port = tk.StringVar()
        self.key_path = tk.StringVar()
        self.select_file_img = tk.PhotoImage(file='./assets/icons8-share-rounded-90.png').subsample(3, 3)

        self.create_text_input(self, "Address IP", self.addr_ip).pack(side="top", fill="x", pady=5, padx=85)
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
        global ADDR_IP
        ADDR_IP = self.addr_ip.get()
        global PORT
        if len(self.port.get()) != 0:
            PORT = self.port.get()
        global KEY_PATH
        KEY_PATH = self.key_path
        global TEXT_VIEW

        thread_comm = Thread(target=try_connect, args=(WORK_MODE, KEY_PATH, PORT, ADDR_IP,))
        thread_comm.start()

        self.controller.show_frame(ConnectFrame, ChatFrame)


class ChatFrame(PanelFrame):
    def __init__(self, container, controller):
        super().__init__(container, controller, 'ChatRoom')
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
        global TEXT_VIEW
        TEXT_VIEW = text_box

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
        chat_bubble("me", text)
        global SOCET
        SOCET.send_msg(text)



def server_side(server_port):
    global SOCET
    SOCET = Server(secure=True)
    try:
        SOCET.start(port=server_port)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        SOCET.socket.close()
        print('Connection closed.')


def client_side(destination, port):
    global SOCET
    SOCET = Client(secure=True)
    try:
        SOCET.connect(destination, port)
    except (Exception, KeyboardInterrupt) as e:
        SOCET.socket.close()
        print('Connection closed.')
        raise


def try_connect(mode: str, key_file, port, address=None):
    global FILENAME
    FILENAME = key_file
    if not port:
        port = 8888
    if mode == "server":
        server_side(int(port))
    elif mode == "client":
        if port and address:
            client_side(address, int(port))
        else:
            raise Exception()
    else:
        print("Error")



BUFFER_SIZE = 1024
ENCODING = 'utf-16'

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
NEW_LINE = '\n'

PRE_TEXT = NEW_LINE + CURSOR_UP_ONE + ERASE_LINE

EXCHANGE_CONFIRMATION = b'***CONFIRMED_EXCHANGE****'

FILENAME = ""


def _print(raw_data):
    print(PRE_TEXT + '>' + raw_data)


def padding(s):
    return s + (((8 - len(s) % 8) - 1) * '~')


def remove_padding(s: str):
    return s.replace('~', '')


def load_auth_key():
    filename = FILENAME
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def save_auth_key(new_auth_key):
    filename = FILENAME
    f = open(filename, "wb")
    f.write(new_auth_key)
    f.close()
    print('Key saved')


class SendMessageBase:
    def _send_message(self, socket, text,):
        if not self.aes:
            self.aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])
        raw_data = text
        if raw_data:
            if self.is_secure:

                data = padding(raw_data).encode(ENCODING)
                encrypted_data = self.aes.encrypt(data)
                #logging.debug('Sending encrypted message: \n%s\n key: %s', encrypted_data,
                #             self.key)
                socket.send(bytes(encrypted_data))
            else:
                socket.send(bytes(raw_data, ENCODING))


class Server(SendMessageBase):
    def __init__(self,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True
                 ):
        self.socket = socket.socket(socket_family, socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = None
        self.key = 'Sixteen byte key'
        self.aes = None
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        print('Exchanging key...')
        chat_bubble('info', 'Exchanging key...')
        #logging.debug('Waiting for public key response...')
        public_key = self.connection.recv(BUFFER_SIZE)
        #logging.debug('Reviced public key: %s', public_key.hex())
        print('Encapsulating key...')
        chat_bubble('info', 'Encapsulating key...')
        shared_secret, ciphertext = self.sike_api.encapsulate(public_key)
        print('Sending cypher text message...')
        chat_bubble('info', 'Sending cypher text message...')
        self.connection.sendall(ciphertext)
        print('Waiting for confirmation...')
        chat_bubble('info', 'Waiting for confirmation...')
        confirmation = self.connection.recv(BUFFER_SIZE)
        if not confirmation == EXCHANGE_CONFIRMATION:
            self.socket.close()
        print('Key exchanged.')
        chat_bubble('info', 'Key exchanged.')

        #logging.debug('Shared secret key is: %s', shared_secret.hex())
        return shared_secret

    def send_msg(self, text):
        self._send_message(self.connection, text)

    def start(self, port):
        self.socket.bind(('', port))
        print('Listening on port %d...', port)
        chat_bubble('info', 'Listening on port ' + str(port) + '...')
        self.socket.listen()
        try:
            self.connection, addr = self.socket.accept()
        except KeyboardInterrupt:
            self.socket.close()
            print('Connection closed.')
            chat_bubble('info', 'Connection Closed')
            sys.exit(1)

        with self.connection:
            print('Connected by %s', addr[0])
            chat_bubble('info', 'Connected by ' + str(addr[0]))
            print("Authorization in progress...")
            chat_bubble('info', 'Authorization in progress...')
            server_auth_key = load_auth_key()
            #logging.debug("Server key OK hash:")
            #logging.debug(server_auth_key)
            client_auth_key = str(self.connection.recv(BUFFER_SIZE), ENCODING)
            #logging.debug("Client key recived")
            if server_auth_key != client_auth_key:
                print('Authorization failed, closing connection')
                chat_bubble('info', 'Authorization failed')
                exit(-1)
            else:
                print('Authorization successful')
                chat_bubble('info', 'Authorization successful')
                self.connection.send(bytes('200', ENCODING))

            aes = None
            if self.is_secure:
                self.key = self.key_exchange()
                save_auth_key(self.key)
                aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])
            try:
                while True:
                    raw_data = self.connection.recv(BUFFER_SIZE)
                    if self.is_secure:
                        #logging.debug('Received encrypted message: %s', raw_data)
                        decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                        chat_bubble("2", decrypted_data)
                        #_print(decrypted_data)
                    else:
                        chat_bubble('2', str(raw_data))
                        _print(raw_data)
                    if not raw_data:
                        break
            except KeyboardInterrupt:
                pass
        self.socket.close()
        print('Connection closed.')
        chat_bubble('info', 'Connection closed')


class Client(SendMessageBase):

    def __init__(self,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True,
                 ):
        self.socket = socket.socket(socket_family, socket_type)
        self.key = 'Sixteen byte key'
        self.aes = None
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        print('Exchanging key...')
        chat_bubble('info', 'Exchanging key')
        #logging.debug('Generating key pair...')
        public_key, secret_key = self.sike_api.generate_key()
        #logging.debug('Generated public key: %s', public_key.hex())
        #logging.debug('Generated secret key: %s', secret_key.hex())

        #logging.debug('Sending public key...')
        self.socket.send(public_key)

        #logging.debug('Waiting for cypher text response...')
        cyphertext_message = self.socket.recv(BUFFER_SIZE)
        #logging.debug('Recived cypher text message: %s', cyphertext_message.hex())
        print('Decapsulating shared key...')
        chat_bubble('info', 'Decapsulating shared key...')
        shared_secret = self.sike_api.decapsulate(secret_key, cyphertext_message)
        self.socket.send(EXCHANGE_CONFIRMATION)
        print('Key exchanged.')
        chat_bubble('info', 'Key exchanged.')
        #logging.debug('Shared secret key is: %s', shared_secret.hex())
        return shared_secret

    def send_msg(self, text):
        self._send_message(self.socket, text)

    def connect(self, destination, port):
        aes = None
        self.socket.connect((destination, port))
        print('Connected with server')
        chat_bubble('info', 'Connected with server')
        print("Authorization in progress...")
        chat_bubble('info', 'Authorization in progress...')
        auth_key = load_auth_key()
        #logging.debug("Client key OK hash:")
        #logging.debug(auth_key)
        self.socket.send(bytes(auth_key, ENCODING))
        #logging.debug("C key sent")
        if str(self.socket.recv(BUFFER_SIZE), ENCODING) != "200":
            print("Authorization failed, closing connection")
            chat_bubble('info', 'Authorization failed')
            exit(-1)
        else:
            print("Authorization successful")
            chat_bubble('info', 'Authorization successful')

        if self.is_secure:
            self.key = self.key_exchange()
            save_auth_key(self.key)
            aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])


        try:
            while True:
                raw_data = self.socket.recv(BUFFER_SIZE)
                if not raw_data:
                    break
                if self.is_secure:
                    #logging.debug('Received encrypted message: %s', raw_data.hex())
                    decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                    chat_bubble("2", decrypted_data)
                    #_print(decrypted_data)
                else:
                    chat_bubble('2', str(raw_data))
                    _print(raw_data)
        except KeyboardInterrupt:
            pass

        self.socket.close()
        print('Connection closed.')
        chat_bubble('info', 'Connection closed')


