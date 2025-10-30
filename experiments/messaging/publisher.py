import zmq, capnp, time
example_capnp = capnp.load('experiments/messaging/example.capnp')

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")

while True:
    msg = example_capnp.Status.new_message(id=1, name="engineTemp", value=87.2)
    pub.send(msg.to_bytes())
    print("sent:", msg)
    time.sleep(1)
