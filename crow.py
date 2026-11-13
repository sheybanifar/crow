import selectors
import socket

selector = selectors.DefaultSelector()

class Connection:

    memebers = {}

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.events = selectors.EVENT_READ
        self.recv_buffer = bytearray()
        self.send_buffer = bytearray()

    def read(self):
        data = self.sock.recv(4096)

        if not data:
            self.close()
            return

        self.recv_buffer += data

        messages = self.parse_buffer()
        for message in messages:
            self.handle_message(message)

        if self.send_buffer:
            self.enable_write()

    def write(self):
        if not self.send_buffer:
            self.disable_write()
            return

        sent = self.sock.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]


    def parse_buffer(self):
        messages = []

        while True:
            if len(self.recv_buffer) < 2:
                break

            payload_length = int.from_bytes(
                self.recv_buffer[:2],
                'big'
            )
            total_length = 2 + payload_length
            if len(self.recv_buffer) < total_length:
                break

            payload = self.recv_buffer[2:total_length]

            self.recv_buffer = self.recv_buffer[total_length:]
            messages.append(payload)

        return messages

    def handle_message(self, message):
        self.send_buffer += message

    def enable_write(self):
        if self.events & selectors.EVENT_WRITE:
            return

        self.events |= selectors.EVENT_WRITE
        selector.modify(
            self.sock,
            self.events,
            data=self
        )

    def disable_write(self):
        if not (self.events & selectors.EVENT_WRITE):
            return

        self.events &= ~selectors.EVENT_WRITE
        selector.modify(
            self.sock,
            self.events,
            data=self
        )

    def close(self):
        selector.unregister(self.sock)
        self.sock.close()



def recv_all(sock: socket.socket):
    pass

def accept_connection(sock: socket.socket):
    client, addr = sock.accept()
    client.setblocking(False)

    connection = Connection(client)

    selector.register(
        client,
        connection.events,
        data=connection
    )

if __name__ == '__main__':

    server = socket.socket()
    server.setblocking(False)
    server.bind(('127.0.0.1', 2001))
    server.listen()

    selector.register(
        server,
        selectors.EVENT_READ,
        data=accept_connection
    )

    while True:
        events = selector.select()

        for key, mask in events:
            if key.fileobj is server:
                accept_connection(key.fileobj)
            else:
                connection = key.data
                if mask & selectors.EVENT_READ:
                    connection.read()
                if mask & selectors.EVENT_WRITE:
                    connection.write()
