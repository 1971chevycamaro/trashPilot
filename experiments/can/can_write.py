# Linux speaks can and has a interface we can attach to to send our data. in this instance we assume that slcand has been run to attach the serial interface
# to the linux CAN stack. when we do that we only need to deal in CAN and slcand takes care of the translation to serial.
import socket, struct, time

CAN_INTERFACE = 'can0'
CAN_ID = 0x100 # if we change the CAN_ID to something the arduino isnt looking for it does nothing but recieve all the serial messages

s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((CAN_INTERFACE,))

def send_led(on: bool):
    data = b'\x01' if on else b'\x00' # were sending a byte 
    s.send(struct.pack("=IB3x8s", CAN_ID, 1, data.ljust(8, b'\x00')))
    print("Sent LED", "ON" if on else "OFF")

# Toggle LED every second
while True:
    send_led(True)
    time.sleep(1)
    send_led(False)
    time.sleep(1)


# candump can0 -> can0  100   [1]  00
# slcand is sending 't100101\r' to the arduino