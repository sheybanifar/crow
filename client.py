import socket
import selectors
import threading

def get_username():
    try:
        while True:
            username = input('Welcome! Enter your name: ')
            return username
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        print('exit!')
        exit()

def get_input(username: str):
    try:
        while True:
            message = input(f'{username}: ')
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        print('exit!')
        exit()

selector = selectors.DefaultSelector()

def first_connect(sock: socket.socket):
    try:
        sock.connect(('127.0.0.1', 2001))
        sock.setblocking(False)
        selector.register(sock, selectors.EVENT_READ)
    except Exception as e:
        print(f'Error: {e}')
        exit()

if __name__ == '__main__':
    username = get_username()
    input_thread = threading.Thread(target=get_input, args=(username,))
    input_thread.start()

    client = socket.socket()
    first_connect(client)

    while True:
        events = selector.select(timeout=3)

        for key, mask in events:
            if mask & selectors.EVENT_READ:
                pass
            if mask & selectors.EVENT_WRITE:
                pass
