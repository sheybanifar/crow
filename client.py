import socket
import selectors
import threading
import queue
import struct

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
            message = input(f'{username}: ').encode()
            user_queue.put(message)
            notifier.sendall(b'1')
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
    
    def get_message(self, user_queue):
        try:
            message = user_queue.get()
            user_queue.task_done()
            return message
        except queue.Empty as e:
            print(e)

    def enable_write(self):
        key = selector.get_key(self.sock)
        if not (key.events & selectors.EVENT_WRITE):
            self.event |= selectors.EVENT_WRITE
            selector.modify(self.sock, self.event, self)

    def populate_sendbuffer(self, user_queue):
        message = self.get_message(user_queue)
        self.send_buffer += message

    def push(self, client: socket.socket, waiter: socket.socket):
        if self.is_closed(waiter):
            return
        
        self.populate_sendbuffer(q)
        self.enable_write()
        sent = client.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

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

def send_username(sock: socket.socket, username: str):
    payload = username.encode()
    payload_len = len(payload)
    header = struct.pack('!H', payload_len)
    packet = header + payload
    sock.sendall(packet)

def first_connect(sock: socket.socket, username):
    try:
        sock.connect(('127.0.0.1', 2001))
        send_username(sock, username)
        sock.setblocking(False)
        conn = Connection(sock)
        selector.register(sock, conn.event, data=conn)
    except Exception as e:
        print(f'Error: {e}')
        exit()

if __name__ == '__main__':
    username = get_username()

    waiter, notifier = socket.socketpair()

    conn = Connection(waiter)
    selector.register(waiter, selectors.EVENT_READ, data=conn)
    
    client = socket.socket()
    first_connect(client, username)

    input_thread = threading.Thread(target=get_input, args=(username, q, notifier))
    input_thread.start()

    while True:
        try:
            events = selector.select(timeout=3)
        except KeyboardInterrupt:
            print('Bye! Bye!')
            exit()

        for key, mask in events:
            if key.fileobj is waiter:
                key_ = selector.get_key(client)
                conn = key_.data
                sent = conn.push(client, key.fileobj)
                print(sent)
            
