import numpy as np
import cv2
from class_webcam_client import FrameClient
from utilities import rgb_to_visionfmt_bilinear as RGBtoVISIONFMT
import time
client = FrameClient()  # attach to shared memory
running = True
while running:
    frame0BGR = client.getFrame()
    time.sleep(0.5) # 20Hz
    frame1BGR = client.getFrame()

    frame_input = np.concatenate([RGBtoVISIONFMT(frame0BGR[:,:,::-1]), RGBtoVISIONFMT(frame1BGR[:,:,::-1])], axis=1)
    np.save("visionfmt.npy", frame_input)
    cv2.imshow("Frame Y", np.concatenate((frame_input[0][0], frame_input[0][6]), axis=1))  # Show in BGR format
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False  # Example condition to exit the loop

client.close()


# rows = [
    # [0,1,2,3,4, 5],    # indices for row 1
    # [6,7,8,9, 10, 11]   # indices for row 2
    # ]
    # grid_rows = [np.hstack([frame_input[0][i] for i in row]) for row in rows]
    # grid = np.vstack(grid_rows)
    # cv2.imshow("Frame Y", grid)  # Show only Y channel for now