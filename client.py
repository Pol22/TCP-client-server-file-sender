import socket
import os
import sys
from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox
import tkinter.ttk as ttk
import time
import threading


buf_size = 1024


class App:
    def __init__(self, master):

        self.label_host = Label(master, text=" Host: ", font="14")
        self.label_host.place(x=5, y=0, height=25, width=40)
        self.txt_host = Text(master, font="14")
        self.txt_host.place(x=45, y=0, height=25, width=180)
        self.txt_host.delete(1.0, END)
        self.txt_host.insert(END, "localhost")

        self.label_port = Label(master, text=" Port: ", font="14")
        self.label_port.place(x=230, y=0, height=25, width=40)
        self.txt_port = Text(master, font="14")
        self.txt_port.place(x=270, y=0, height=25, width=60)
        self.txt_port.delete(1.0, END)
        self.txt_port.insert(END, "9090")

        self.button_connect = Button(master, text="Connect",
                                     command=self.connect)
        self.button_connect.place(x=335, y=0)
        self.connect_checker = Radiobutton(master, text="", variable=1,
                                           fg="red")
        self.connect_checker.place(x=400, y=5)

        self.txt = Text(master, font="14")
        self.txt.place(x=5, y=30, width=490, height=25)
        self.ask_open_button = Button(master, text="Open",
                                      command=self.open_file)
        self.ask_open_button.place(x=455, y=0)
        self.txt.delete(1.0, END)
        self.txt.insert(END, "Path of file")
        self.send_button = Button(master, text="Send",
                                  command=self.send_file_app)
        self.send_button.place(x=0, y=60)

        self.progress = ttk.Progressbar(master, orient='horizontal',
                                        length=200, mode='determinate')
        self.progress.place(x=5, y=100)
        self.progress["value"] = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.thread_send = threading.Thread()

        self.kill = False

    def open_file(self):
        of = askopenfilename()
        self.txt.delete(1.0, END)
        self.txt.insert(END, of)

    def send_file(self, name):
        try:
            self.socket.send(name.encode("utf-8"))
            self.socket.recv(2)
            self.socket.send(str(os.path.getsize(name)).encode("utf-8"))
            len = self.socket.recv(buf_size)
            file = open(name, 'rb')
            file.seek(int(len.decode("utf-8")))
            self.progress["value"] += int(len.decode("utf-8"))
            self.progress["maximum"] = os.path.getsize(name)
            while True:
                data = file.read(buf_size)
                if not data:
                    break
                self.socket.send(data)
                self.progress["value"] += buf_size
            self.socket.close()
            file.close()
        except:
            messagebox.showinfo("Socket error", "Connetction failure")
            self.progress["value"] = 0
            self.connect_checker["fg"] = "red"

    def send_file_app(self):
        name = str(self.txt.get(1.0, END)).replace('\n', '')
        try:
            pr = os.open(name, os.O_RDONLY)
            os.close(pr)
        except:
            messagebox.showinfo("File error", "Can't open file'")
            return
        if self.connect_checker["fg"] == "green":
            self.thread_send = threading.Thread(target=self.send_file,
                                                kwargs={'name': name})
            self.thread_send.daemon = True
            self.thread_send.start()
        else:
            messagebox.showinfo("Connection error", "Connetction failure")
            return

    def connect(self):
        host = str(self.txt_host.get(1.0, END)).replace('\n', '')
        port = int(str(self.txt_port.get(1.0, END)).replace('\n', ''))
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connect_checker["fg"] = "green"
        except:
            self.connect_checker["fg"] = "red"
            self.socket.close()
            messagebox.showinfo("Connection error", "Can't connect to server")

    def close(self):
        root.destroy()
        self.kill = True
        self.socket.close()
        root.quit()


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.wm_title('Client')
    root.minsize(width=500, height=500)
    root.protocol('WM_DELETE_WINDOW', app.close)
    root.mainloop()
