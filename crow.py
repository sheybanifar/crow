import selectors
import socket

selector = selectors.DefaultSelector()

def accept_connection(sock: socket.socket):
    if sock is server:
        client, addr = sock.accept()
        client.setblocking(False)

        selector.register(
            client,
            selectors.EVENT_READ,
            data=read_connection
        )

def read_connection(sock: socket.socket):
    data = sock.recv(4096)
    if not data:
        selector.unregister(sock)
        sock.close()

server = socket.socket()
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
        callback = key.data
        callback(key.fileobj)