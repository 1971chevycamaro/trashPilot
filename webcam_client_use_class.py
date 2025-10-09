# consumer.py
import cv2
from class_webcam_client import FrameClient

client = FrameClient()  # attach to shared memory

while True:

    cv2.imshow("Shared Frame", client.frameStream)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        client.close()
        break
    # time.sleep(0.5)
    
cv2.destroyAllWindows()