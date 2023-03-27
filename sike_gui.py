import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd, messagebox, Scrollbar, Text
from threading import Thread
import comunication.mim as mim

WORK_MODE = None

ADDR_IP = None
PORT = None
KEY_PATH = None

TEXT_VIEW = None

Lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sem lacus, varius vel pellentesque vel, consectetur eget lectus. Etiam at libero et lacus ornare faucibus a sed lorem. Etiam eleifend sem ac semper molestie. Maecenas pharetra posuere mauris dapibus interdum. Nunc vel nulla quam. Pellentesque cursus lobortis nibh, et efficitur ligula commodo nec. Aliquam libero nisi, commodo porttitor ipsum et, venenatis suscipit turpis. Quisque tempus nisl urna, ut bibendum nunc sagittis a. Nulla imperdiet, lorem eu aliquet tempor, est leo fermentum sapien, cursus viverra odio urna vitae quam. Nam sit amet nisl sed magna volutpat imperdiet."


def frame_changer(frame_name):
    frame_name.tkraise()

'''
def threadStarter():
    # TODO errors

    global WORK_MODE
    global KEY_PATH
    global ADDR_IP
    print(WORK_MODE)
    print(KEY_PATH)
    print(ADDR_IP)
    thread_comm = Thread(target=mim.try_connect, args=(WORK_MODE, KEY_PATH, PORT, ADDR_IP,))
    thread_comm.start()
'''

def chat_bubble(sender, text: str):
    global TEXT_VIEW
    TEXT_VIEW.config(state='normal')
    if sender == "me":
        TEXT_VIEW.insert('end', "\n\n\tME -->")
    else:
        TEXT_VIEW.insert('end', "\n\tBOB-->")
    TEXT_VIEW.insert('end', "\n" + text)
    TEXT_VIEW.config(state='disabled')

def send_message():
    pass

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

        thread_comm = Thread(target=mim.try_connect, args=(WORK_MODE, KEY_PATH, PORT, ADDR_IP,))
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
            # TODO command=,
            style="FI.TButton"
        )
        send_button.pack(side="right")

