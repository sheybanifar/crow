import selectors
import socket

selector = selectors.DefaultSelector()

class Connection:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.events = selectors.EVENT_READ
        self.recv_buffer = bytearray()
        self.send_buffer = bytearray()

    def read(self):
        pass

    def write(self):
        pass

def accept_connection(sock: socket.socket):
    if sock is server:
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
                elif mask & selectors.EVENT_WRITE:
                    connection.write()
