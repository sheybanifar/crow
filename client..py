import socket
import selectors
import threading

def get_input():
    try:
        while True:
            return input('User: ')
    except (EOFError, KeyboardInterrupt):
        return

selector = selectors.DefaultSelector()

def connection(sock: socket.socket):
    sock.connect(('127.0.0.1', 2001))


# events = selectors.EVENT_READ | selectors.EVENT_WRITE


if __name__ == '__main__':
    client = socket.socket()
    client.setblocking(False)

    selector.register(client, selectors.EVENT_WRITE)
    
    client.connect(('127.0.0.1', 2001))
    
    events = selector.select(timeout=3)

    for key, mask in events:
        if mask & selectors.EVENT_WRITE:
