import time
import capnp  # generated file from schema
sensor_capnp = capnp.load('experiments/messaging/sensor.capnp')


with open('hello','rb') as f:
    
    for addresses in sensor_capnp.SensorReading.read_multiple(f):
        print(addresses)
        time.sleep(1)
    # msg.read
    # print(msg.humidity)
