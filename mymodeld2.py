import class_messaging as messaging
import time
import numpy as np
import onnxruntime as ort
from utilities import BGR2YYYYUV
from class_webcam_client import FrameClient
import class_transform
import cv2
import can
bus = can.interface.Bus(
    channel='can0', 
    interface='socketcan',
    can_filters=[{"can_id": 0x440, "can_mask": 0x7FF}]
    )

def on_message(msg):
  global vEgo 
  vEgo = msg.data[2]*.28
notifier = can.Notifier(bus, [on_message])

client = FrameClient()  # attach to shared memory
drivingPolicy = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_policy.onnx")
drivingVision = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_vision.onnx")
visionModelInputs = { # allocate inputs (if we made an array each time it would be slow so we allocate and reuse)
    "img": np.zeros((1, 12, 128, 256), dtype=np.uint8),
    "big_img": np.zeros((1, 12, 128, 256), dtype=np.uint8)
} 
policyModelInputs = {
  'desire': np.zeros((1, 25, 8), dtype=np.float16),
  'traffic_convention': np.zeros((1, 2), dtype=np.float16),
  'lateral_control_params': np.zeros((1, 2), dtype=np.float16),
  'prev_desired_curv': np.zeros((1, 25, 1), dtype=np.float16),
  'features_buffer': np.zeros((1, 25, 512), dtype=np.float16),
}
visionModelOutputs = np.zeros((1, 632), dtype=np.float32)
policyModelOutputs = np.zeros((1,5884), dtype=np.float32)
H = class_transform.H # i dont want to have to change the same transform everywhere
H1 =  H
pm = messaging.PubMaster("modelV2")
sm = messaging.SubMaster('carState')
period = 0.20
frame1BGR = client.getFrame()
while True:
  start = time.perf_counter()
  frame0BGR = frame1BGR
  # time.sleep(0.05) # 20Hz
  frame1BGR = client.getFrame()
  # vEgo = 15.0 
  actuatorDelay = 0.2
  # print(BGR2YYYYUV(cv2.warpPerspective(frame0BGR, H, (512,256),flags=cv2.INTER_NEAREST)).shape)
  visionModelInputs["img"][0, 0:6, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame0BGR, H, (512,256),flags=cv2.INTER_NEAREST))
  visionModelInputs["img"][0, 6:12, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame1BGR, H, (512,256),flags=cv2.INTER_NEAREST))   
  # visionModelInputs["big_img"][0, 0:6, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame0BGR, H1, (512,256),flags=cv2.INTER_NEAREST)) 
  # visionModelInputs["big_img"][0, 6:12, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame1BGR, H1, (512,256),flags=cv2.INTER_NEAREST)) 
  visionModelInputs["big_img"] = visionModelInputs["img"] # just duplicate for now
  # np.save("img.npy", visionModelInputs["img"])
  policyModelInputs['desire'][0] = 0
  policyModelInputs['traffic_convention'][0] = [0.0, 1.0]  # RHD
  policyModelInputs['lateral_control_params'][0] = [vEgo, actuatorDelay]
  policyModelInputs['prev_desired_curv'][0, :-1] = policyModelInputs['prev_desired_curv'][0, 1:] # shift left
  policyModelInputs['prev_desired_curv'][0, -1,:] = policyModelOutputs[0][5880:5882][0] # model only uses last value now
  policyModelInputs['features_buffer'][0, :-1] = policyModelInputs['features_buffer'][0, 1:] # shift left
  policyModelInputs['features_buffer'][0, -1] = visionModelOutputs[0][117:629]  # hidden_state slice
  
  visionModelOutputs[:] = drivingVision.run(None, visionModelInputs)[0]
  policyModelOutputs[:] = drivingPolicy.run(None,policyModelInputs)[0]
  # print(policyModelOutputs[0][5880:5882][1])
  # print(policyModelInputs['prev_desired_curv'])
  pm.send({'laneLines': policyModelOutputs[0][4955:5483].tolist(), 'action': policyModelOutputs[0][5880:5882].tolist()}) 
  elapsed = time.perf_counter() - start
  sleep_time = period - elapsed
  if sleep_time > 0:
    time.sleep(sleep_time)
  # print(1/(time.perf_counter() - start))
  # print(vEgo)
  # print(policyModelOutputs[0][5880:5882][1])
  # print(policyModelInputs['features_buffer'][0,:,0]) # hidden_state slice
  # print(policyModelOutputs[0][4955:5483].tolist())
  print(policyModelOutputs[0][5880:5882][0])
