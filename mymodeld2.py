# example: build policy numpy_inputs with concrete ONNX shapes
import numpy as np
import onnxruntime as ort
from utilities import BGR2YYYYUV
from class_webcam_client import FrameClient
import time
import cv2
client = FrameClient()  # attach to shared memory
drivingPolicy = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_policy.onnx")
drivingVision = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_vision.onnx")
visionModelInputs = { # allocate inputs (if we made an array each time it would be slow so we allocate and reuse)
    "img": np.empty((1, 12, 128, 256), dtype=np.uint8),
    "big_img": np.empty((1, 12, 128, 256), dtype=np.uint8)
} 
policyModelInputs = {
  'desire': np.empty((1, 25, 8), dtype=np.float16),
  'traffic_convention': np.empty((1, 2), dtype=np.float16),
  'lateral_control_params': np.empty((1, 2), dtype=np.float16),
  'prev_desired_curv': np.empty((1, 25, 1), dtype=np.float16),
  'features_buffer': np.empty((1, 25, 512), dtype=np.float16),
}
visionModelOutputs = np.empty((1, 632), dtype=np.float16)
policyModelOutputs = np.empty((1,5884), dtype=np.float16)

H = np.array([[2.9322348e+00, 1.5542418e-02, 1.5469591e+02],
 [1.4313864e-02, 2.9198198e+00, 4.2012244e+02],
 [2.3892755e-05, 1.7017686e-05, 9.9271709e-01]], np.float32)

while True:
  frame0BGR = client.getFrame()
  time.sleep(0.05) # 20Hz
  frame1BGR = client.getFrame()
  vEgo = 10.0 
  actuatorDelay = 0.1
  print(BGR2YYYYUV(cv2.warpPerspective(frame0BGR, H, (512,256),flags=cv2.INTER_NEAREST)).shape)
  visionModelInputs["img"][0, 0:6, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame0BGR, H, (512,256),flags=cv2.INTER_NEAREST))
  visionModelInputs["img"][0, 6:12, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame1BGR, H, (512,256),flags=cv2.INTER_NEAREST))   
  visionModelInputs["big_img"] = visionModelInputs["img"] # just duplicate for now

  policyModelInputs['desire'][0] = 0
  policyModelInputs['traffic_convention'][0] = [0.0, 1.0]  # RHD
  policyModelInputs['lateral_control_params'][0] = [vEgo, actuatorDelay]
  policyModelInputs['prev_desired_curv'][0, :-1] = policyModelInputs['prev_desired_curv'][0, 1:] # shift left
  policyModelInputs['prev_desired_curv'][0, -1] = policyModelOutputs[0][5880:5882][1] # model only uses last value now
  policyModelInputs['features_buffer'][0, :-1] = policyModelInputs['features_buffer'][0, 1:] # shift left
  policyModelInputs['features_buffer'][0, -1] = visionModelOutputs[0][117:629]  # hidden_state slice
  
  visionModelOutputs[:] = drivingVision.run(None, visionModelInputs)[0]
  policyModelOutputs[:] = drivingPolicy.run(None,policyModelInputs)[0]
  print(policyModelInputs['features_buffer'][0,:,0]) # hidden_state slice
