import socket
import selectors
import threading

def get_username():
    try:
        while True:
            username = input('Welcome! Enter your name: ')
            return username
    except (EOFError, KeyboardInterrupt):
        print('exit!')
        return

def get_input(username: str):
    try:
        while True:
            return input(f'{username}: ')
    except (EOFError, KeyboardInterrupt):
        print('exit!')
        return

selector = selectors.DefaultSelector()

def first_connect(sock: socket.socket):
    try:
        connected = not bool(sock.connect_ex(('127.0.0.1', 2001)))
        if connected:
            print('Connected!')
            selector.register(sock, selectors.EVENT_READ)
        else:
            print('Error: ', connected)
    except Exception as e:
        print(f'Unexpected error was occured!\n', e)

if __name__ == '__main__':
    username = get_username()
    input_thread = threading.Thread(target=get_input, args=(username,))
    input_thread.start()

    client = socket.socket()
    client.setblocking(False)
    
    first_connect(client)

    while True:
        events = selector.select(timeout=3)

        for key, mask in events:
            if mask & selectors.EVENT_READ:
                pass
            if mask & selectors.EVENT_WRITE:
                pass
