import cv2
import numpy as np
from multiprocessing import shared_memory
import time

cap = cv2.VideoCapture("/home/skylo/Desktop/IMG_2229.MOV")
already_sharing = False 

try:
    while True:
        ret, frame = cap.read()
        shape = np.array(frame.shape, dtype=np.int16)
        if not already_sharing:
            try:
                shapeshm = shared_memory.SharedMemory(create=True, size=shape.nbytes, name="shape")
                frameshm = shared_memory.SharedMemory(create=True, size=frame.nbytes, name="frame")
            except FileExistsError:
                shapeshm = shared_memory.SharedMemory(create=False, name="shape")
                frameshm = shared_memory.SharedMemory(create=False, name="frame")
                already_sharing = True
        # Write frame and shape bytes to shared memory (not exactly efficient, but it is readable)
        shapeshm.buf[:shape.nbytes] = shape.tobytes()
        frameshm.buf[:frame.nbytes] = frame.tobytes()
        time.sleep(1/cap.get(cv2.CAP_PROP_FPS)) # 20Hz
except KeyboardInterrupt:
    print("Exiting...")
    cap.release()
    frameshm.unlink()
    shapeshm.unlink()