import class_messaging as messaging
import time
import numpy as np
import onnxruntime as ort
from utilities import BGR2YYYYUV
from class_webcam_client import FrameClient
import class_transform
import cv2
import zmq
import capnp
class ModelRunner:
  def __init__(self):
    self.drivingPolicy = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_policy.onnx")
    self.drivingVision = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_vision.onnx")
    self.visionModelInputs = { # allocate inputs (if we made an array each time it would be slow so we allocate and reuse)
        "img": np.zeros((1, 12, 128, 256), dtype=np.uint8),
        "big_img": np.zeros((1, 12, 128, 256), dtype=np.uint8)
    } 
    self.policyModelInputs = {
      'desire': np.zeros((1, 25, 8), dtype=np.float16),
      'traffic_convention': np.zeros((1, 2), dtype=np.float16),
      'lateral_control_params': np.zeros((1, 2), dtype=np.float16),
      'prev_desired_curv': np.zeros((1, 25, 1), dtype=np.float16),
      'features_buffer': np.zeros((1, 25, 512), dtype=np.float16),
    }
    self.visionModelOutputs = np.zeros((1, 632), dtype=np.float32)
    self.policyModelOutputs = np.zeros((1,5884), dtype=np.float32)
    
  def run(self,newFrame,vEgo,actuatorDelay):
    self.visionModelInputs["img"][0, 0:6, :, :] = self.visionModelInputs["img"][0, 6:12, :, :]
    self.visionModelInputs["img"][0, 6:12, :, :] = newFrame   
    self.visionModelInputs["big_img"] = self.visionModelInputs["img"] 
    self.policyModelInputs['desire'][0] = 0
    self.policyModelInputs['traffic_convention'][0] = [0.0, 1.0]  # RHD
    self.policyModelInputs['lateral_control_params'][0] = [vEgo, actuatorDelay]
    self.policyModelInputs['prev_desired_curv'][0, :-1] = self.policyModelInputs['prev_desired_curv'][0, 1:] # shift left
    self.policyModelInputs['prev_desired_curv'][0, -1,:] = self.policyModelOutputs[0][5880:5882][0] # model only uses last value now
    self.policyModelInputs['features_buffer'][0, :-1] = self.policyModelInputs['features_buffer'][0, 1:] # shift left
    self.policyModelInputs['features_buffer'][0, -1] = self.visionModelOutputs[0][117:629]  # hidden_state slice
    
    self.visionModelOutputs[:] = self.drivingVision.run(None, self.visionModelInputs)[0]
    self.policyModelOutputs[:] = self.drivingPolicy.run(None,self.policyModelInputs)[0]

client = FrameClient()  # attach to shared memory
models = [ModelRunner(),ModelRunner()]
period = 1/(len(models)*5)


H = class_transform.H # i dont want to have to change the same transform everywhere
H1 =  H
pm = messaging.PubMaster("modelV2")
vEgo = 10.0

# Subscribe to vEgo published by mycarcontroller.py (capnp Status on tcp://localhost:5556)
example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context.instance()
sub = ctx.socket(zmq.SUB)
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.setsockopt(zmq.CONFLATE, 1)
sub.connect("tcp://localhost:5556")
while True:
  for model in models:
    start = time.perf_counter()
    # Non-blocking read of latest vEgo
    try:
      raw = sub.recv(flags=zmq.NOBLOCK)
      with example_capnp.Event.from_bytes(raw) as msg:
        vEgo = msg.carState.vEgo
    except zmq.Again:
      pass
    frame0 = BGR2YYYYUV(cv2.warpPerspective(client.frameStream, H, (512,256),flags=cv2.INTER_NEAREST))
    model.run(frame0,vEgo,0.2)
    pm.send({'laneLines': model.policyModelOutputs[0][4955:5483].tolist(), 'action': model.policyModelOutputs[0][5880:5882].tolist()}) 
    elapsed = time.perf_counter() - start
    sleep_time = period - elapsed
    if sleep_time > 0:
      time.sleep(sleep_time)
    print(f"{1/(time.perf_counter() - start):.2f} Hz\r", end="")
    # print(vEgo)
