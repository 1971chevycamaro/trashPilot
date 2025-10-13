import serial
import time
import class_messaging as messaging
sm = messaging.SubMaster('modelV2')
# open serial connection to Arduino
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
time.sleep(2)  # wait for Arduino reset

def send_value(x):
    x = max(-1, min(1, x))  # clamp to -1..1
    ser.write(f"{x:.3f}\n".encode())

# example test
while True:
    if sm.updated():
        val = sm.data()['action'][0]
        # print(val*10)
        # val = float(input("Enter value (-1 to 1): "))
        send_value(val*30)
