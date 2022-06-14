

def generate_opcode_message(sender: str = '', recipient: str = '', data: str = ''):
    message = ''
    message += '0' if sender == '' else '1'
    message += '0' if recipient == '' else '1'
    message += '0' if data == '' else '1'
    message += "{0:0=2d}{1}".format(len(sender), sender)
    message += "{0:0=2d}{1}".format(len(recipient), recipient)
    message += "{0:0=3d}{1}".format(len(data), data)

    print("Generated: " + message)
    return message


def handle_opcode_message(data: str):
    try:
        print("handling: " + data)
    except TypeError:
        print('handling ')
    sender = ''
    if int(data[0]):
        length = int(data[3:5])
        for index in range(0, length):
            sender += data[5 + index]
    else:
        sender = 'SERVER'

    recipient = ''
    if int(data[1]):
        length = int(data[5 + len(sender):7 + len(sender)])
        for index in range(0, length):
            recipient += data[7 + len(sender) + index]

    message = ''
    if int(data[2]):
        length = int(data[8 + len(sender) + len(recipient):10 + len(sender) + len(recipient)])
        for index in range(0, length):
            message += data[10 + len(sender) + len(recipient) + index]

    return sender, recipient, message


def verify_server_handshake(handshake: str):
    opcode = handshake[0:3]
    if opcode != '000':
        return 0, []
    else:
        handshake = handshake.replace('000', '')
        users = handshake.split()
        return 1, users


def verify_client_handshake(handshake: str):
    opcode = handshake[0:3]
    if opcode != '000':
        return 0, []
    else:
        length = int(handshake[3:5])
        name = ''
        for index in range(0, length):
            name += handshake[5 + index]
        return 1, name
