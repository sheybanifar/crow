import selectors
import socket

selector = selectors.DefaultSelector()

def accept_connection(sock: socket.socket):
    pass

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
        if key.fileobj is server:
            accept_connection(server)
        else:
            pass