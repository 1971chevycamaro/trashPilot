# frame_client.py
import numpy as np
from multiprocessing import shared_memory, resource_tracker

class FrameClient:
    def __init__(self, frame_name="frame", shape_name="shape"):
        """Attach to existing shared memory for frame and shape"""
        self.frameshm = shared_memory.SharedMemory(name=frame_name)
        self.shapeshm = shared_memory.SharedMemory(name=shape_name)
        # Avoid automatic unlink by resource_tracker
        resource_tracker.unregister(self.frameshm._name, 'shared_memory')
        resource_tracker.unregister(self.shapeshm._name, 'shared_memory')
        # Read shape from shared memory
        shape = np.frombuffer(self.shapeshm.buf, dtype=np.int16)
        self.shape = tuple(shape)
        # Create numpy view on frame data
        self.frameStream = np.ndarray(self.shape, dtype=np.uint8, buffer=self.frameshm.buf)

    def getFrame(self):
        """Return a new BGR array for the current frame"""
        return self.frameStream.copy()

    def close(self):
        """Close shared memory without unlinking"""
        self.frameshm.close()
        self.shapeshm.close()
