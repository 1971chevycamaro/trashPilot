import onnxruntime as ort
import numpy as np
from utilities import BGR2YYYYUV
from class_webcam_client import FrameClient
import time
import class_transform
import cv2
# Load ONNX model
client = FrameClient()  # attach to shared memory
frame1BGR = client.frameStream

drivingVision = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_vision.onnx")
visionModelInputs = { # allocate inputs (if we made an array each time it would be slow so we allocate and reuse)
    "img": np.zeros((1, 12, 128, 256), dtype=np.uint8),
    "big_img": np.zeros((1, 12, 128, 256), dtype=np.uint8)
} 
visionModelOutputs = np.zeros((1, 632), dtype=np.float32)
H = class_transform.H # i dont want to have to change the same transform everywhere
H1 =  H

# Inference loop run @ 20Hz
period = 0.05  # 20Hz
while True:
  start = time.perf_counter()
  visionModelInputs["img"][0, 0:6, :, :] = visionModelInputs["img"][0, 6:12, :, :]
  visionModelInputs["img"][0, 6:12, :, :] = BGR2YYYYUV(cv2.warpPerspective(frame1BGR, H, (512,256),flags=cv2.INTER_NEAREST))   
  cv2.imshow("input", np.hstack((visionModelInputs["img"][0, 0:6, :, :][0] , visionModelInputs["img"][0, 6:12, :, :][0])))
  elapsed = time.perf_counter() - start
  sleep_time = period - elapsed
  if sleep_time > 0:
    if cv2.waitKey(int(sleep_time*1000)) == 27:
      break  # Exit on ESC key
  print(f"{1/(time.perf_counter() - start):.2f} Hz\r", end="")


#     {
#   'model_checkpoint': ...,
#   'output_slices': {
#     'meta': slice(0, 55, None),
#     'desire_pred': slice(55, 87, None),
#     'pose': slice(87, 99, None),
#     'wide_from_device_euler': slice(99, 105, None),
#     'road_transform': slice(105, 117, None),
#     'hidden_state': slice(117, 629, None),
#     'pad': slice(-3, None, None)
#   },
#   'input_shapes': {...},
#   'output_shapes': {'outputs': (1, 632)}
# }
client.close()