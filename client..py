import socket
import selectors
import threading

selector = selectors.DefaultSelector()

def establish_connection(sock):
    sock

client = socket.socket()
client.setblocking(False)
# client.connect(('127.0.0.1', 2001))

event = selectors.EVENT_READ | selectors.EVENT_WRITE

selector.register(client, event,)