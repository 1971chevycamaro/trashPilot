import can
import time
bus = can.interface.Bus(
    channel='can0', 
    interface='socketcan',
    can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
    )
def on_message(msg):
    print(msg.data[2])

notifier = can.Notifier(bus, [on_message])
while True:
    time.sleep(1)
