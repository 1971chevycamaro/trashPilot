# messaging.py
import zmq
import json
import threading
import time

class PubMaster:
    def __init__(self, topic, port=5556):
        self.topic = topic
        ctx = zmq.Context.instance()
        self.sock = ctx.socket(zmq.PUB)
        self.sock.bind(f"tcp://*:{port}")

    def send(self, data):
        # topic prefix allows selective subscription
        self.sock.send_string(self.topic, zmq.SNDMORE)
        self.sock.send_json(data)


class SubMaster:
    def __init__(self, topic, address="localhost", port=5556):
        self.topic = topic
        ctx = zmq.Context.instance()
        self.sock = ctx.socket(zmq.SUB)
        self.sock.connect(f"tcp://{address}:{port}")
        self.sock.setsockopt_string(zmq.SUBSCRIBE, topic)
        self._latest = None
        self._updated = False
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            topic = self.sock.recv_string()
            msg = self.sock.recv_json()
            self._latest = msg
            self._updated = True

    def update(self):
        self._updated = False

    def updated(self):
        return self._updated

    def data(self):
        return self._latest
    

# from messaging import PubMaster
# import time

# pm = PubMaster('laneLines')
# while True:
#     pm.send({'x': [0,1,2], 'y': [3,4,5]})
#     time.sleep(0.05)

# or

# from messaging import SubMaster
# import time

# sm = SubMaster('laneLines')
# while True:
#     if sm.updated():
#         data = sm.data()
#         print("Got:", data)
#         sm.update()
#     time.sleep(0.01)

