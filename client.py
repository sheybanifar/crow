import socket
import selectors
import threading
import queue
import struct
from enum import IntEnum

selector = selectors.DefaultSelector()
q = queue.Queue()

HEADER_STRUCT = struct.Struct('!BQ')

class MessageType(IntEnum):
    WAKE_UP = 1
    SEND_USERNAME = 2

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
        for _ in range(limit):
            try:
                message = user_queue.get_nowait().encode()
            except queue.Empty:
                break

            self.send_buffer.extend(message)
            user_queue.task_done()

    def enable_write(self):
        key = selector.get_key(self.sock)
        if not (key.events & selectors.EVENT_WRITE):
            self.event |= selectors.EVENT_WRITE
            selector.modify(self.sock, self.event, self)

    # def populate_sendbuffer(self, user_queue):
    #     message = self.get_message(user_queue)
    #     self.send_buffer += message

    def push(self, waiter: socket.socket):
        if self.is_closed(waiter):
            return
        
        # self.populate_sendbuffer(q)
        self.enable_write()
        sent = self.sock.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

        if len(self.send_buffer) == 0:
            self.event = selectors.EVENT_READ
            selector.modify(self.sock, self.event, self)

        return sent

    def is_closed(self, waiter: socket.socket):
        data = waiter.recv(1024)
        if not data:
            selector.unregister(waiter)
            selector.unregister(self.sock)
            waiter.close()
            self.sock.close()
            return True
        else:
            return False

def make_package(msg_type: MessageType, payload):
    payload = payload.encode()
    payload_len = len(payload)
    header = HEADER_STRUCT.pack(msg_type, payload_len)
    package = header + payload

    return package

def send_username(sock: socket.socket, username: str):
    payload = username.encode()
    payload_len = len(payload)
    header = struct.pack('!H', payload_len)
    packet = header + payload
    sock.sendall(packet)

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

    input_thread = threading.Thread(target=get_input, args=(username, q, notifier))
    input_thread.start()

    while True:
        events = selector.select(timeout=3)

        for key, mask in events:
            if key.fileobj is waiter:
                if not drain_wakeup(waiter):
                    # Manage Shutdown
                    pass
                conn_client = selector.get_key(client).data
                conn_client.get_message(q)
                print(conn_client.send_buffer)
            else:
                conn = key.data
                if mask & selectors.EVENT_WRITE:
                    pass
                if mask & selectors.EVENT_READ:
                    pass

            # if key.fileobj is waiter:
            #     key_ = selector.get_key(client)
            #     conn = key_.data
            #     sent = conn.push(client, key.fileobj)
            #     print(sent)
            
