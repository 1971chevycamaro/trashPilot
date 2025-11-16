import zmq
import capnp
import time
example_capnp = capnp.load('experiments/messaging/example.capnp')

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5558")

while True:
    msg = example_capnp.Event.new_message()
    msg.logMonotime = int(time.monotonic() * 1000)
    msg.init('carControl').actuators.torque = 1.5
    pub.send(msg.to_bytes())
    print("sent:", msg)
    time.sleep(1)
