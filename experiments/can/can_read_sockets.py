# Linux speaks can and has a interface we can attach to to send our data. in this instance we assume that slcand has been run to attach the serial interface
# to the linux CAN stack. when we do that we only need to deal in CAN and slcand takes care of the translation to serial.
import socket
import struct
import numpy as np

CAN_INTERFACE = 'can0'
CAN_ID = 0x123

s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((CAN_INTERFACE,))

while True:
    frame = s.recv(16)
    can_id, dlc, data = struct.unpack("=IB3x8s", frame)

    if can_id == CAN_ID:
        print(np.uint8(data[2]))

# sudo slcand -S 115200 ttyACM0 can0 && sudo ifconfig can0 up
# candump can0

