import class_messaging as messaging
import can
import time
# pm = messaging.PubMaster('carState')
sm = messaging.SubMaster('modelV2')
bus = can.interface.Bus(
    channel='can0', 
    interface='socketcan',
    can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
    )
# def on_message(msg):
#     pm.send({'carState': {
#         'vEgo': msg.data[2]*.28
#     }})

# notifier = can.Notifier(bus, [on_message])
dir = 0
msg = can.Message(
    arbitration_id=0x363,
    is_extended_id=False
)
# example test
while True:
    if sm.updated():
        val = sm.data()['action'][0]
        # Determine direction
        effort = abs(int((val*3000)))
        if val>0:
            dir = 1
        else:
            dir = 2
        # clamp effort to [0, 255] just in case
        effort = max(0, min(150, effort))
        print([effort, dir])
        # print(abs(int((val*15000))))
        msg.data = [effort, dir]
        bus.send(msg)
        time.sleep(0.1)

