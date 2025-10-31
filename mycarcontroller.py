import os
import can
import time
import zmq
import capnp

example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5558")
sub.setsockopt_string(zmq.SUBSCRIBE, "")

# Check if can0 exists
can_available = os.path.exists('/sys/class/net/can0')

bus = None
if can_available:
    bus = can.interface.Bus(
        channel='can0',
        interface='socketcan',
        can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
    )
else:
    print("!!! can0 not found — printing instead of sending")

msg = can.Message(
    arbitration_id=0x363,
    is_extended_id=False
)

while True:
    raw = sub.recv()
    with example_capnp.Status.from_bytes(raw) as torque_msg:
        val = torque_msg.value
        effort = abs(int((val / 12 * 250)))
        dir = 2 if val > 0 else 1
        effort = max(0, min(150, effort))
        msg.data = [effort, dir]

        if can_available:
            bus.send(msg)
        else:
            print("bus send", [effort, dir])

        # time.sleep(0.1)
