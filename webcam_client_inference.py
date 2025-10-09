import onnxruntime as ort
import numpy as np
from utilities import rgb_to_visionfmt_bilinear as RGBtoVISIONFMT
from class_webcam_client import FrameClient
import time
# Load ONNX model
client = FrameClient()  # attach to shared memory
drivingVision = ort.InferenceSession("onnx_test/driving_vision.onnx")
drivingPolicy = ort.InferenceSession("onnx_test/driving_policy.onnx")
visionModelInputs = {
        "img": np.zeros((1,12,128,256), dtype=np.uint8), 
        "big_img": np.zeros((1,12,128,256), dtype=np.uint8)
        } # i could fix the BGR->RGB to work natively but meh
policyModelInputs = {
        'desire': np.empty((1,25,8), dtype=np.float16),
        'traffic_convention': np.empty((1,2), dtype=np.float16),
        'lateral_control_params': np.empty((1,2), dtype=np.float16),
        'prev_desired_curv': np.empty((1,25,1), dtype=np.float16),
        'features_buffer': np.empty((1,25,512), dtype=np.float16),
        }
visionModelOutputs = np.empty((1, 632), dtype=np.float16)

running = True
# Inference loop run @ 20Hz
period = 0.05  # 20Hz
while running:
    start = time.perf_counter()
    frame0BGR = client.getFrame()
    time.sleep(0.05) # 20Hz
    frame1BGR = client.getFrame()
    visionModelInputs["img"][0, 0:6, :, :] = RGBtoVISIONFMT(frame0BGR)
    visionModelInputs["img"][0, 6:12, :, :] = RGBtoVISIONFMT(frame1BGR)   
    visionModelInputs["big_img"] = visionModelInputs["img"] # just duplicate for now
     # Run the model
    

    visionModelOutputs[:] = drivingVision.run(None, visionModelInputs)[0]
    print(visionModelOutputs[0,105:117]) # zero out road_transform for now

    # full_features_buffer[0,:-1] = full_features_buffer[0,1:]
    # full_features_buffer[0,-1] = vision_outputs_dict['hidden_state'][0, :]
    # numpy_inputs['features_buffer'][:] = full_features_buffer[0, self.temporal_idxs]
    
    #print("vision model visionModelOutputs:", visionModelOutputs[0][0][117:629]) # hidden_state slice
    # keep the 20Hz loop
    # while time.perf_counter() - start <= period:
    #     pass
    # # track time Hz
    # print("vision model Hz:", 1/(time.perf_counter() - start))



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