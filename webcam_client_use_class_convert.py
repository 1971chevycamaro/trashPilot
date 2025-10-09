import numpy as np
import cv2
from class_webcam_client import FrameClient
# from conversions import RGB2YUV

client = FrameClient()  # attach to shared memory
# math to crop to 2:1 aspect ratio
width = client.shape[1]
height = int(width/2) # desired height
margin = int((client.shape[0] - height) / 2) # top & bottom px margins

running = True

while running:

    frame = client.getFrame()
    formattedIMG = cv2.resize(frame[margin:client.shape[0]-margin], (512, 256))
    formattedIMG_YUV = cv2.cvtColor(formattedIMG, cv2.COLOR_BGR2YUV_I420)

    VISIONFMT = np.zeros((1,6, 128, 256), dtype=np.uint8)
    VISIONFMT[0][0] = formattedIMG_YUV[0:256,:][0::2,0::2]
    VISIONFMT[0][1] = formattedIMG_YUV[0:256,:][1::2,0::2]
    VISIONFMT[0][2] = formattedIMG_YUV[0:256,:][0::2,1::2]
    VISIONFMT[0][3] = formattedIMG_YUV[0:256,:][1::2,1::2]
    VISIONFMT[0][4] = formattedIMG_YUV[256:,:][64:].reshape(128,256)
    VISIONFMT[0][5] = formattedIMG_YUV[256:,:][:64].reshape(128,256)

    cv2.imshow("Frame Y", formattedIMG)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        client.close()
        running = False

client.close()
cv2.destroyAllWindows()

