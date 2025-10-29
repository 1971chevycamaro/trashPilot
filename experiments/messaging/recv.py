import socket
with socket.socket() as s:
    s.connect(('localhost', 5000))
    while True:
        data = s.recv(5)
        print(data)
        if not data:
            break
    # print(s.recv(1024))
    # print(s.recv(1024))
    # print(s.recv(1024))
    # --- IGNORE ---