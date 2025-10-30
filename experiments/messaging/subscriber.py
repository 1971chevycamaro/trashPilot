import zmq, capnp
example_capnp = capnp.load('experiments/messaging/example.capnp')

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    raw = sub.recv()
    with example_capnp.Status.from_bytes(raw) as msg:
        print(f"got: id={msg.id}, name={msg.name}, value={msg.value}")
