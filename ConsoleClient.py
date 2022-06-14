# This is a console version of the client.

import _thread
import socket
import sys


def listen_for_input(client: socket):
    while True:
        message = input("")
        if not message: continue
        message = '[101][' + name + '] ' + message
        client.send(message.encode())


def verify_handshake(handshake: str):
    if len(handshake) <= 5:
        return False
    op_code = handshake[0:5]
    if op_code == '[000]':
        return True
    else:
        return False


def check_op_code(message: str):
    op_code = message[0:5]
    match op_code:
        case '[101]':
            print(message.replace('[101]', ''))
        case '[404]':
            pass
            # Error

# Check if custom IP and PORT are provided.
if len(sys.argv) >= 3:
    IP = sys.argv[1]
    PORT = sys.argv[2]
else:
    print('Please enter IP and PORT as arguments.')
    sys.exit(1)

# Request a nickname.
name = input('Nickname: ')

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, PORT))

# Handshake upon connecting.
# handshake = '[000] Attempt Connect'
# client.send(handshake.encode())
handshake = client.recv(4096).decode()
if verify_handshake(handshake):
    welcome_message = '[SERVER] Welcome to the server {}!\t-\tConnections: {}'.format(name, handshake.split(':')[1])
    handshake = '[000]{}'.format(name)
    client.send(handshake.encode())
    print(welcome_message)
else:
    print('Handshake failed, connection aborted.')
    sys.exit(1)

# start a thread for listening for input to send
_thread.start_new_thread(listen_for_input, (client,))

# Start loop for listening
while True:
    server_message = client.recv(4096).decode()
    if not server_message: break
    check_op_code(server_message)

# Close connection at the end.
client.close()
