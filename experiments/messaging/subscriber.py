import zmq
import capnp
import time
example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.setsockopt(zmq.CONFLATE, 1)
sub.connect("tcp://localhost:5558")


while True:
    # try:
    # raw = sub.recv(flags=zmq.NOBLOCK)
    raw = sub.recv()
    with example_capnp.Event.from_bytes(raw) as msg:
        print(msg.carControl.actuators.torque)
    # except zmq.Again:
    #     pass
    
    time.sleep(.5)