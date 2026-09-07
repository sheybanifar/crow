import socket

connection = socket.socket()
connection.connect(('127.0.0.1', 2001))

while True:
    msg = input('write anything: ')
    connection.sendall(msg.encode())

    response = connection.recv(4096).decode()

    if not response:
        print('Disconnect!')
        connection.close()
        break