import socket
import selectors
import threading
import queue

selector = selectors.DefaultSelector()
q = queue.Queue()

def get_username():
    try:
        while True:
            username = input('Welcome! Enter your name: ')
            return username
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        print('exit!')
        exit()

def get_input(username: str, user_queue, sock: socket.socket):
    try:
        while True:
            message = input(f'{username}: ').encode()
            user_queue.put(message)
            sock.sendall(b'1')
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        print('exit!')
        exit()

def get_message(user_queue):
    try:
        message = user_queue.get()
        user_queue.task_done()
        return message
    except queue.Empty as e:
        print(e)

class Connection:
    def __init__(self, sock):
        self.sock = sock
        self.event = selectors.EVENT_READ
        self.send_buffer = bytearray()
    
    def enable_write(self):
        key = selector.get_key(self.sock)
        if not (key.events & selectors.EVENT_WRITE):
            self.event |= selectors.EVENT_WRITE
            selector.modify(self.sock, self.event, self)

    def push(sock, msg):
        pass
    
    # @classmethod
    # def prepare_to_send(cls, callback, sock: socket.socket, user_queue):
    #     message = callback(user_queue)
    #     cls.send_buffer += message
    #     key = selector.get_key(sock)
    #     if not (key.events & selectors.EVENT_WRITE):
    #         key.events |= selectors.EVENT_WRITE
    #         selector.modify(sock, )


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

    waiter, notifier = socket.socketpair()
    selector.register(waiter, selectors.EVENT_READ, data=get_message)
    
    client = socket.socket()
    first_connect(client)

    input_thread = threading.Thread(target=get_input, args=(username, q, notifier))
    input_thread.start()

    while True:
        events = selector.select(timeout=3)

        for key, mask in events:
            if key.fileobj is waiter:
                callback = key.data
                message = callback(q)
            else:
                if mask & selectors.EVENT_READ:
                    pass
                if mask & selectors.EVENT_WRITE:
                    pass
