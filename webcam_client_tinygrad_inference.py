from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes
import pickle
import numpy as np
from utilities import rgb_to_visionfmt_bilinear as RGBtoVISIONFMT
from class_webcam_client import FrameClient
import time
import os
os.environ['GPU'] = '1'
os.environ['IMAGE'] = '0'
# Load ONNX model
client = FrameClient()  # attach to shared memory
drivingVision = pickle.load(open("/home/skylo/openpilot/selfdrive/modeld/models/big_driving_vision_tinygrad.pkl", "rb"))
# drivingPolicy = ort.InferenceSession("onnx_test/driving_policy.onnx")
running = True
# Inference loop run @ 20Hz
period = 0.05  # 20Hz
while running:
    start = time.perf_counter()
    frame0BGR = client.getFrame()
    time.sleep(0.05) # 20Hz
    frame1BGR = client.getFrame()

    visionModelInputs = {
        "img": Tensor(np.concatenate([RGBtoVISIONFMT(frame0BGR[:,:,::-1]), RGBtoVISIONFMT(frame1BGR[:,:,::-1])], axis=1), dtype=dtypes.uint8).realize(), 
        "big_img": Tensor(np.concatenate([RGBtoVISIONFMT(frame0BGR[:,:,::-1]), RGBtoVISIONFMT(frame1BGR[:,:,::-1])], axis=1), dtype=dtypes.uint8).realize()
        } # i could fix the BGR->RGB to work natively but meh
    policyModelInputs = {
        'desire': np.zeros((1,25,8), dtype=np.float16),
        'traffic_convention': np.zeros((1,2), dtype=np.float16),
        'lateral_control_params': np.zeros((1,2), dtype=np.float16),
        'prev_desired_curv': np.zeros((1,25,1), dtype=np.float16),
        'features_buffer': np.zeros((1,25,512), dtype=np.float16),
        }

    visionModelOutputs = drivingVision(**visionModelInputs)

    # keep the 20Hz loop
    while time.perf_counter() - start <= period:
        pass
    # track time Hz
    # print("vision model Hz:", 1/(time.perf_counter() - start))
client.close()