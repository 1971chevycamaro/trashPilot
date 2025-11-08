import cv2
import numpy as np
import class_transform
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

# H = class_transform.H
H = np.array([[2.9319131e+00, 1.6042843e-02, 1.5560883e+02],
       [1.4114303e-02, 2.9201300e+00, 4.1882837e+02],
       [2.3538028e-05, 1.7569415e-05, 9.9278069e-01]], dtype=np.float32)
H = np.linalg.inv(H)
# invert the H since were going from source dimensions to dest dimensions

corners = get_warp_corners(H, 512, 256)
# print(corners)
H = np.linalg.inv(H)
img = cv2.imread("assets/samples/visionipc.png")

vis = draw_focus_region(img, corners)
cv2.namedWindow("focus", cv2.WINDOW_NORMAL)
cv2.imshow("focus", vis)
cv2.waitKey(0)
while True:
    vis = draw_focus_region(img, corners)

    cv2.imshow("warped", BGR2YYYYUV(cv2.warpPerspective(img, H, (512,256),flags=cv2.INTER_NEAREST + cv2.WARP_INVERSE_MAP))[0])
    if cv2.waitKey(1)== 27:
        break  # Exit on ESC key
cv2.destroyAllWindows()