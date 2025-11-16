import os
import can
import time
import zmq
import capnp

example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context()
# SUB: torque commands
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5558")
sub.setsockopt_string(zmq.SUBSCRIBE, "")

# PUB: vehicle state (vEgo) -> model consumers
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")


# Check if can0 exists
can_available = os.path.exists('/sys/class/net/can0')
if can_available:
    bus = can.interface.Bus(
        channel='can0',
        interface='socketcan',
        can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
    )
vEgo = 13

while True:
    try: # look for a torque message
        raw = sub.recv(flags=zmq.NOBLOCK)

        with example_capnp.Status.from_bytes(raw) as torque_msg:
            val = torque_msg.value
            effort = abs(int((val / 12 * 250)))
            dir = 2 if val > 0 else 1
            effort = max(0, min(110, effort))
            msg = can.Message(
                arbitration_id=0x363,
                is_extended_id=False,
                data = [effort, dir]
                )
            if can_available:
                bus.send(msg)
            else:
                print("bus send", [effort, dir])
    except zmq.Again:
        pass
        time.sleep(0.1)
    # m = bus.recv(timeout=0.0)
    # vEgo += 1

    msg = example_capnp.Event.new_message()
    msg.logMonoTime = int(time.monotonic() * 1000)
    car_state = msg.init('carState')

    car_state.vEgo = vEgo 

    pub.send(msg.to_bytes())

# sudo slcand -S 115200 ttyACM0 can0 && sudo ifconfig can0 up 
# candump can0