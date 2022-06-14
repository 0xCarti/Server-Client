import socket
import _thread
import sys
import OperationCode as oc
import requests


def broadcast_message(message: str, recipient: str = None):
    for (conn, addr, name) in clients_list:
        if recipient is None:
            conn.send(message.encode())
        else:
            if recipient == name:
                conn.send(message.encode())


def broadcast_data(data: str):
    for (conn, addr, name) in clients_list:
        conn.send(data.encode())


def verify_handshake(handshake: str):
    if len(handshake) <= 5:
        return False
    op_code = handshake[0:5]
    if op_code == '[000]':
        return True
    else:
        return False


def check_op_code(sender: str, recipient: str, message: str):
    opcode = ''
    opcode += '0' if sender == '' else '1'
    opcode += '0' if recipient == '' else '1'
    opcode += '0' if message == '' else '1'
    print("Checking: " + opcode)
    match opcode:
        case '000':  # NA
            pass
        case '001':  # NA
            pass
        case '010':  # NA
            pass
        case '100':  # connect
            pass
        case '101':  # Client broadcast
            message = oc.generate_opcode_message(sender=sender, data=message)
            broadcast_message(message=message)
        case '110':  # Client to Client poke
            message = oc.generate_opcode_message(sender=sender, data='just poked you!')
            broadcast_message(message, recipient)
        case '011':  # Server to Client message
            message = oc.generate_opcode_message(recipient=recipient, data=message)
            broadcast_message(message, recipient)
        case '111':  # Client to Client message
            message = oc.generate_opcode_message(sender=sender, recipient=recipient, data=message)
            broadcast_message(message, recipient)
        case '[404]':  # Error OP
            pass


def print_connections():
    output = '[SERVER] Connections: {}\n'.format(len(clients_list))
    for (conn, addr) in clients_list:
        output += '\t- {}'.format(addr)
    print(output)


def listen_for_commands():
    while True:
        command = input("")
        if not command: continue
        if command[0] != '/':
            print('[SERVER] No prefix detected. Try adding a "/"')
            continue
        command = command.replace('/', '')
        match command:
            case 'users':
                print_connections()
            case 'help':
                pass
                # Print all commands.
            case _:
                print('[SERVER] "{}" is not recognized as a valid command. Try /help.'.format(command))


def on_new_client(connection, address):
    # Handshake with new connection
    handshake = '000'  # [000]:[conn1]:[conn2]:[conn n]
    for (conn, addr, name) in clients_list:
        handshake += '{}:'.format(name)
    connection.send(handshake.encode())
    handshake = connection.recv(4096).decode()
    while not handshake:
        handshake = connection.recv(4096).decode()
    valid, name = oc.verify_client_handshake(handshake)
    if valid:
        opcode = oc.generate_opcode_message(sender=name)
        # broadcast_message(message)
        clients_list.append((connection, address, name))

        # data = '[111] {}'.format(name)
        broadcast_data(opcode)
        print('[INFO] New Connection: {} - {}'.format(address, name))

    # Listen for incoming messages and check code for action.
    while True:
        try:
            client_message = connection.recv(4096).decode()
            if not client_message: break
            sender, recipient, message = oc.handle_opcode_message(client_message)
            check_op_code(sender, recipient, message)
        except ConnectionResetError:  # Connection was terminated by client.
            break

    # Close and remove connection when nothing came in.
    connection.close()
    for (conn, addr, name) in clients_list:
        if addr == address:
            clients_list.remove((conn, addr, name))
            print('[INFO] Disconnected: {} - {}'.format(address, name))


clients_list = []

# Check args for custom IP and PORT.
if len(sys.argv) >= 3:
    IP = sys.argv[1]
    PORT = sys.argv[2]
else:
    print('Please enter IP and PORT as arguments.')
    sys.exit(1)


# Bind server to socket and listen for 5 incoming connections
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((IP, PORT))
serv.listen(5)

# Start the command thread
_thread.start_new_thread(listen_for_commands, ())

# Get the public ip of the socket.
PUBLIC_IP = requests.get('https://api.ipify.org/').text

print('[SERVER] Server started!\t-\t[{}:{}]'.format(PUBLIC_IP, PORT))

while True:
    # Accept any new connection that comes in and start thread for it
    conn, addr = serv.accept()
    _thread.start_new_thread(on_new_client, (conn, addr))
