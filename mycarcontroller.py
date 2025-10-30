# import class_messaging as messaging
import can
import time
import zmq
import capnp
example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")

# pm = messaging.PubMaster('carState')
# bus = can.interface.Bus(
#     channel='can0', 
#     interface='socketcan',
#     can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
#     )
# def on_message(msg):
#     pm.send({'carState': {
#         'vEgo': msg.data[2]*.28
#     }})

# notifier = can.Notifier(bus, [on_message])
dir = 0
# msg = can.Message(
#     arbitration_id=0x363,
#     is_extended_id=False
# )
# example test
while True:
    raw = sub.recv()
    with example_capnp.Status.from_bytes(raw) as torque_msg:

        val = torque_msg.value
        # Determine direction
        effort = abs(int((val/12*150)))
        if val>0:
            dir = 1
        else:
            dir = 2
        # clamp effort to [0, 255] just in case
        effort = max(0, min(150, effort))
        print([effort, dir])
        # print(abs(int((val*15000))))
        # msg.data = [effort, dir]
        # bus.send(msg)
        # time.sleep(0.1)
