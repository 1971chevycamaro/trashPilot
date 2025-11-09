#!/usr/bin/env python3
import class_messaging as messaging
import cv2
import numpy as np
from class_webcam_client import FrameClient

# === CONFIG ===
client = FrameClient()

SCALE = 6         # pixels per meter
WIDTH, HEIGHT = client.shape[1], client.shape[0]
print(WIDTH,HEIGHT)
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT - 50
MAX_X = 200       # meters forward to display
FPS = 20

def world_to_img(x, y):
    """Convert (x forward, y left) in meters to image coordinates"""
    u = int(CENTER_X + y * SCALE)
    v = int(CENTER_Y - x * SCALE)
    return u, v

def draw_lane(img, x, y, color):
    pts = [world_to_img(xi, yi) for xi, yi in zip(x, y)]
    for i in range(1, len(pts)):
        cv2.line(img, pts[i-1], pts[i], color, 2, cv2.LINE_AA)

def main():
    sm = messaging.SubMaster('modelV2')
    # laneLines.x = laneLines
    while True:
        # img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
        img = client.getFrame()
        if sm.updated():
            arr = sm.data()['laneLines']
            arr = np.array(arr[0:264][0::2])
            lanes = arr.reshape((4,33))
            # lanes[0] left most lane y values only
            for i in range(4):
                x = np.array([0, 0.1875, 0.75, 1.6875, 3, 4.6875, 6.75, 9.1875, 12, 15.1875, 18.75, 22.6875, 27, 31.6875, 36.75, 42.1875, 48, 54.1875, 60.75, 67.6875, 75, 82.6875, 90.75, 99.1875, 108, 117.1875, 126.75, 136.6875, 147, 157.6875, 168.75, 180.1875, 192])       # forward distance indices
                y = lanes[i]*4                     # lateral positions
                color = [(255,0,0),(0,255,0),(0,255,255),(0,0,255)][i]
                draw_lane(img, x, y, color)
            # sm.update()   

        cv2.imshow("Lane Lines", img)

        if cv2.waitKey(int(1000/FPS)) == 27:  # ESC to quit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
