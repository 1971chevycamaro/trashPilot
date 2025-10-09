# consumer.py
import numpy as np
from multiprocessing import resource_tracker, shared_memory
import cv2

# Attach to existing shared memory
shapeshm = shared_memory.SharedMemory(name="shape")
frameshm = shared_memory.SharedMemory(name="frame")
resource_tracker.unregister(shapeshm._name, 'shared_memory') # Ensure it is not unlinked on close
resource_tracker.unregister(frameshm._name, 'shared_memory') # Ensure it is not unlinked on close

shape = np.ndarray((3,), dtype=np.int16, buffer=shapeshm.buf)
frame = np.ndarray(tuple(shape), dtype=np.uint8, buffer=frameshm.buf)

while True:
    cv2.imshow("Shared Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        shapeshm.close()
        frameshm.close()
        break
    
cv2.destroyAllWindows()