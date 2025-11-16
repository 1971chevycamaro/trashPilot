import zmq
import capnp
import time
example_capnp = capnp.load('experiments/messaging/example.capnp')

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")

while True:
    msg = example_capnp.CarControl.new_message()
    msg.actuators.torque = 1.5
    pub.send(msg.to_bytes())
    print("sent:", msg)
    time.sleep(1)
