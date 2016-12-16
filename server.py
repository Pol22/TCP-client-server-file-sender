import socket
import threading
import time
from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox
import tkinter.ttk as ttk


buf_size = 1024
max_clients = 1


class App(object):
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

        self.button_connect = Button(master, text="Start",
                                     command=self.start_server)
        self.button_connect.place(x=335, y=0)
        self.connect_checker = Radiobutton(master, text="", variable=1,
                                           fg="red")
        self.connect_checker.place(x=400, y=5)

        self.txt = Text(master, font="14")
        self.txt.place(x=5, y=30, width=490, height=25)
        self.ask_open_button = Button(master, text="Open",
                                      command=self.save_file)
        self.ask_open_button.place(x=455, y=0)
        self.txt.delete(1.0, END)
        self.txt.insert(END, os.getcwd())

        self.progress = ttk.Progressbar(master, orient='horizontal',
                                        length=200, mode='determinate')
        self.progress.place(x=5, y=100)
        self.progress["value"] = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client = socket.socket()

        self.thread_accept = threading.Thread()

    def save_file(self):
        sf = askdirectory()
        if(sf):
            self.txt.delete(1.0, END)
            self.txt.insert(END, sf)

    def start_server(self):
        host = str(self.txt_host.get(1.0, END)).replace('\n', '')
        port = int(str(self.txt_port.get(1.0, END)).replace('\n', ''))
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((host, port))
            self.socket.listen(max_clients)
            self.connect_checker["fg"] = "green"
            self.thread_accept = threading.Thread(target=self.accept_file)
            self.thread_accept.daemon = True
            self.thread_accept.start()
        except:
            self.connect_checker["fg"] = "red"
            self.socket.close()
            self.socket_client.close()
            messagebox.showinfo("Start error", "Connetction failure")

    def accept_file(self):
        self.socket_client, addr = self.socket.accept()
        print('connected: ', addr)
        try:
            name = self.socket_client.recv(buf_size)
            name = name.decode("utf-8").split('/')[-1]
            self.socket_client.send(b'ok')
            data_len = self.socket_client.recv(buf_size)
            file_size = int(data_len.decode("utf-8"))
            self.progress["maximum"] = file_size
            file_dir = str(self.txt.get(1.0, END)).replace('\n', '')
            size = 0
            if name in os.listdir(file_dir):
                size = os.path.getsize(file_dir + "\\" + name)
            else:
                size = 0
            self.socket_client.send(str(size).encode("utf-8"))
            self.progress["value"] += size
            file = open(file_dir + '\\' + name, 'wb')
            file.seek(size)
            while True:
                data = self.socket_client.recv(buf_size)
                if not data:
                    break
                file.write(data)
                self.progress["value"] += buf_size
            file.close()
        except:
            messagebox.showerror("Socket error", "Connetction failure")
            self.progress["value"] = 0
            return
        finally:
            #self.progress["value"] += buf_size
            if self.progress["value"] >= self.progress["maximum"]:
                messagebox.showinfo("Received file", file_dir+'\\'+name)
            else:
                messagebox.showerror("Connection error", "Connetction failure")
                self.progress["value"] = 0

    def close(self):
        root.destroy()
        self.socket.close()
        self.socket_client.close()
        root.quit()


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.wm_title('Server')
    root.minsize(width=500, height=500)
    root.protocol('WM_DELETE_WINDOW', app.close)
    root.mainloop()
