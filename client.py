import socket
import selectors
import threading
import queue
import struct
from enum import IntEnum

selector = selectors.DefaultSelector()
q = queue.Queue()

def get_username():
    try:
        while True:
            username = input('Welcome! Enter your name: ')
            if validate_username(username):
                return username
            else:
                print('Invalid username! correct it.')
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        print('exit!')
        exit()

def validate_username(username: str):
    username = username.strip()

    if username != '' and len(username) <= 30:
        return username
    else:
        return False

def get_input(username: str, user_queue, notifier: socket.socket):
    try:
        while True:
            message = input(f'{username}: ').strip()
            if message:
                user_queue.put(message)
            notifier.send(b'1')
    except (EOFError, KeyboardInterrupt):
        # experimental. terminating the program must be implemented in future.
        exit()
    finally:
        notifier.close()

class Connection:
    def __init__(self, sock):
        self.sock = sock
        self.event = selectors.EVENT_READ
        self.send_buffer = bytearray()
    
    def get_message(self, user_queue, limit: int = 50):
        for i in range(limit):
            try:
                message = user_queue.get_nowait().encode()
            except queue.Empty:
                return False

            self.send_buffer.extend(message)
            user_queue.task_done()
            
            if i == limit - 1:
                return not user_queue.empty()

        return False

def first_connect(sock: socket.socket):
    try:
        sock.connect(('127.0.0.1', 2001))
        sock.setblocking(False)
        conn = Connection(sock)
        selector.register(sock, conn.event, data=conn)
    except Exception as e:
        print(f'Error: {e}')
        exit()

def drain_wakeup(waiter):
    while True:
        try:
            data = waiter.recv(4096)

            if not data:
                return False
        
        except BlockingIOError:
            break

    return True

if __name__ == '__main__':
    username = get_username()

    waiter, notifier = socket.socketpair()

    waiter.setblocking(False)
    notifier.setblocking(False)

    conn = Connection(waiter)
    selector.register(waiter, conn.event, data=conn)
    
    client = socket.socket()
    first_connect(client)
    client_conn = selector.get_key(client).data

    input_thread = threading.Thread(target=get_input, args=(username, q, notifier))
    input_thread.start()

    pending_messages = False

    while True:
        timeout = 0 if pending_messages else 3
        events = selector.select(timeout)

        for key, mask in events:
            if key.fileobj is waiter:
                if not drain_wakeup(waiter):
                    # Manage Shutdown; implement in future...
                    break

                pending_messages = True

        if pending_messages:
            pending_messages = client_conn.get_message(q)

            # else:
            #     conn = key.data
            #     if mask & selectors.EVENT_WRITE:
            #         pass
            #     if mask & selectors.EVENT_READ:
            #         pass
