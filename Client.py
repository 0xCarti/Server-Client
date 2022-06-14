import socket
import sys
import OperationCode as oc
from tkinter import *


def verify_handshake(handshake: str):
    if len(handshake) <= 5:
        return False
    op_code = handshake[0:5]
    if op_code == '000':
        return True
    else:
        return False


def start_connection(name: str, chatbox: Text, connection_box: Text):
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('PLACE IP HERE', 65535))

    # Receive and verify the handshake
    handshake = client.recv(4096).decode()
    valid, users = oc.verify_server_handshake(handshake)
    if valid:
        welcome_message = '[SERVER] Welcome to the server {}!'.format(name)
        chatbox.configure(state='normal')
        chatbox.insert(END, welcome_message + '\n')
        chatbox.configure(state='disabled')
        # handshake = handshake.replace('[000]', '')
        connection_box.configure(state='normal')
        for user in users:
            if user == '':
                continue
            connection_box.insert(END, user + '\n')
        connection_box.configure(state='disabled')
        handshake = '000{0:0=2d}{1}'.format(len(name), name)
        client.send(handshake.encode())
        return client
    else:
        chatbox.configure(state='normal')
        chatbox.insert(END, 'Handshake failed, connection aborted.')
        chatbox.configure(state='disabled')
        sys.exit(1)
