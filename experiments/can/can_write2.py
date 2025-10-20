import can
import time

bus = can.interface.Bus(channel='can0', interface='socketcan')

msg = can.Message(
    arbitration_id=0x363,
    is_extended_id=False
)
bus.send(msg)
    # print(msg)

while True:
    msg.data = [80,1]  # forward, small effort
    bus.send(msg)
    time.sleep(0.5)