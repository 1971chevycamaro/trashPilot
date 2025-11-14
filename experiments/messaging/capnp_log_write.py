import time
import capnp  # generated file from schema
sensor_capnp = capnp.load('experiments/messaging/sensor.capnp')

with open('hello','wb') as f:
    msg = sensor_capnp.SensorReading.new_message()
    msg.humidity = 12.34
    msg.timestamp = int(time.monotonic() * 1000)
    msg.write(f)
