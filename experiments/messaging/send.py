import socket
import time
with socket.socket() as s:
    s.bind(('localhost',5000))
    s.listen(1)
    hostaddr,port = s.accept()
    print(hostaddr.getsockname()[0])
    hostaddr.send(b'hello')
    hostaddr.send(b'hello')
    time.sleep(1)
    hostaddr.send(b'hello')
    hostaddr.send(b'there')
    hostaddr.close()
