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
    selector.register(waiter, selectors.EVENT_READ)
    
    client = socket.socket()
    first_connect(client)

    input_thread = threading.Thread(target=get_input, args=(username, q, notifier))
    input_thread.start()

    while True:
        events = selector.select(timeout=3)

        for key, mask in events:
            if key.fileobj is waiter:
                user_message = get_message(q)
                print(user_message)
                # selector.unregister(waiter)
            else:
                if mask & selectors.EVENT_READ:
                    pass
                    # if not (data := key.fileobj.recv()):
                    #     key.fileobj.close()
                if mask & selectors.EVENT_WRITE:
                    pass
