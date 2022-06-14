import _thread
import tkinter as tk
from tkinter.simpledialog import askstring

import OperationCode as oc
from tkinter import *
import Client

WIDTH = 550
HEIGHT = 450


def create_new_window(title: str, root: Tk, sizex: int = WIDTH, sizey: int = HEIGHT):
    new_window = Toplevel(root)
    new_window.title(title)
    new_window.geometry('{}x{}'.format(str(sizex), str(sizey)))
    new_window.resizable(width=False, height=False)


def update_textbox(box: Text, data: str, isPM=False, isServer = False):
    if isPM:
        box.configure(state='normal')
        lines = box.index('end-1c').split('.')[0]
        box.insert(tk.END, data + '\n')
        box.tag_config('PM', foreground="blue")
        box.tag_add('PM', '{}.0'.format(lines), '{}.{}'.format(lines, len(data)))
        box.configure(state='disabled')
    elif isServer:
        box.configure(state='normal')
        lines = box.index('end-1c').split('.')[0]
        box.insert(tk.END, data + '\n')
        box.tag_config('Server', foreground="red")
        box.tag_add('Server', '{}.0'.format(lines), '{}.{}'.format(lines, len(data)))
        box.configure(state='disabled')
    else:
        box.configure(state='normal')
        box.insert(tk.END, data + '\n')
        box.configure(state='disabled')


def update_connections_list(connections: list):
    chat_box.delete(0, END)
    for connection in connections:
        chat_box.insert(END, connection + '\n')


def send_message_button():
    message = input_box.get()
    opcode = oc.generate_opcode_message(sender=name, data=message)
    client.send(opcode.encode())
    input_box.delete(0, tk.END)


def send_pmessage_button():
    try:
        recipient = member_display_box.selection_get()
    except TclError:
        return

    message = input_box.get()
    opcode = oc.generate_opcode_message(sender=name, recipient=recipient, data=message)
    client.send(opcode.encode())
    input_box.delete(0, tk.END)


def listen_for_message():
    # Start loop for listening
    while True:
        server_message = client.recv(4096).decode()
        if not server_message: break
        sender, recipient, message = oc.handle_opcode_message(server_message)
        check_op_code(sender, recipient, message)
    # Close connection at the end.
    client.close()


def check_op_code(sender: str, recipient: str, message: str):
    opcode = ''
    opcode += '0' if sender == '' else '1'
    opcode += '0' if recipient == '' else '1'
    opcode += '0' if message == '' else '1'
    match opcode:
        case '000':  # Incoming handshake
            users = message.replace('000', '').split()
            for index in range(0, len(users)):
                update_textbox(member_display_box, users[index])
        case '001':  # Server broadcast
            message = '[{}]: {}'.format(sender, message)
            update_textbox(chat_box, message, isServer=True)
        case '010':  # Server kicked Client
            pass
        case '100':  # connect
            message = '[{}]: CONNECTED'.format(sender)
            update_textbox(chat_box, message)
            update_textbox(member_display_box, sender)
        case '101':  # Client broadcast
            message = '[{}]: {}'.format(sender, message)
            update_textbox(chat_box, message)
        case '110':  # Client to Client poke
            message = '{} poked you!'.format(sender, message)
            update_textbox(chat_box, message, isPM=True)
        case '011':  # Server to Client message
            message = '[{}]: {}'.format(sender, message)
            update_textbox(chat_box, message, isServer=True)
        case '111':  # Client to Client message
            message = '[{}]: {}'.format(sender, message)
            update_textbox(chat_box, message, isPM=True)
        case '[404]':  # Error OP
            pass


gui = Tk(className="Chatroom")
gui.title("Chatroom")
gui.geometry('{}x{}'.format(str(WIDTH), str(HEIGHT)))
gui.resizable(width=False, height=False)

# Create the chat box to display messages from clients
chat_box = Text(gui, bg='#F4F2EB')
chat_box.configure(state='disabled')
# chat_box.pack(padx=(0, 2), side=tk.LEFT, anchor=tk.NW)
chat_box.place(x=5, y=5, width=(WIDTH - 20) * .65, height=(HEIGHT - 19 - 20))

# Create a member display box to show connected users.
member_display_box = Text(gui)
member_display_box.configure(state='disabled')
# member_display_box.pack(padx=(2, 0), side=tk.RIGHT, anchor=tk.NE)
member_display_box.place(x=(WIDTH * .65), y=5, width=(WIDTH - 20) * .35, height=(HEIGHT - 70))

# Create a text box for message input
input_box = Entry(gui)
input_box.focus()
input_box.place(x=5, y=(HEIGHT - 25 - 5), width=(WIDTH - 20) * .65, height=25)

# Create a bottom for sending private messages
send_pmessage_button = Button(gui, text='Private Message', command=send_pmessage_button)
send_pmessage_button.place(x=(WIDTH * .65), y=(HEIGHT - 60), width=(WIDTH - 20) * .35, height=25)

# Create a bottom for sending messages
send_message_button = Button(gui, text='Send Message', command=send_message_button)
send_message_button.place(x=(WIDTH * .65), y=(HEIGHT - 30), width=(WIDTH - 20) * .35, height=25)

name = askstring("", "Enter Nickname", parent=gui)

client = Client.start_connection(name, chat_box, member_display_box)
_thread.start_new_thread(listen_for_message, ())

# Start the GUI loop
gui.lift()
gui.attributes('-topmost', True)
gui.after_idle(gui.attributes, '-topmost', False)
gui.mainloop()
