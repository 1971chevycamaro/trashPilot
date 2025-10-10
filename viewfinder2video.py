import cv2
import numpy as np
from utilities import BGR2YYYYUV

def get_warp_corners(H, width, height):
    """
    Returns the 4 source coordinates (float32)
    that map to the corners of a warpPerspective
    output of size (width x height).

    H: 3x3 homography matrix
    width, height: dimensions of the output image
    """
    dst_corners = np.array([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ], dtype=np.float32)

    pts = np.hstack([dst_corners, np.ones((4,1), np.float32)])  # -> (4,3)
    src = (np.linalg.inv(H) @ pts.T).T
    src /= src[:, [2]]
    return src[:, :2]

def draw_focus_region(img, pts, color=(0,255,0), alpha=0.50):
    """
    Draws a polygon around pts on img.
    Everything outside is dimmed.
    pts: array-like of shape (4,2) — polygon corners.
    """
    overlay = img.copy()
    mask = np.zeros_like(img, np.uint8)
    pts = np.array(pts, np.int32).reshape((-1,1,2))
    cv2.fillPoly(mask, [pts], (255,255,255))
    dimmed = cv2.addWeighted(img, alpha, np.zeros_like(img), 1-alpha, 0)
    result = dimmed.copy()
    result[mask[:,:,0] > 0] = img[mask[:,:,0] > 0]
    cv2.polylines(result, [pts], True, color, 2)
    return result
quad = [(100,100), (400,120), (380,300), (80,280)]

H = np.array([[1, 0, 50],
 [0, 1, 80],
 [0, 0, 1]], np.float32)
# invert the H since were going from source dimensions to dest dimensions
H = np.linalg.inv(H)
corners = get_warp_corners(H, 512, 256)
# print(corners)

# img = cv2.imread("assets/samples/visionipc.png")
cap = cv2.VideoCapture('assets/samples/videoexample.mp4')
ret, img = cap.read()
vis = draw_focus_region(img, corners)
cv2.namedWindow("focus", cv2.WINDOW_NORMAL)
cv2.imshow("focus", vis)
cv2.waitKey(0)
while True:
    ret, img = cap.read()
    if not ret:
        break
    vis = draw_focus_region(img, corners)

    cv2.imshow("warped", BGR2YYYYUV(cv2.warpPerspective(img, H, (512,256),flags=cv2.INTER_NEAREST))[0])
    if cv2.waitKey(30) == 27:
        break  # Exit on ESC key
cap.release()
cv2.destroyAllWindows()