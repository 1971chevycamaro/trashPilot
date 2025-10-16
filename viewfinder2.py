# viewfinder2.py
import cv2
import numpy as np

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

img = cv2.imread("assets/samples/visionipc.png")

cv2.namedWindow("focus", cv2.WINDOW_NORMAL)
cv2.resizeWindow("focus", 900, 600)

def nothing(x): pass
cv2.createTrackbar("tx", "focus", 0, 1000, nothing)
cv2.createTrackbar("ty", "focus", 0, 1000, nothing)
cv2.createTrackbar("scale", "focus", 100, 400, nothing)
cv2.createTrackbar("rot", "focus", 0, 360, nothing)

width, height = 512, 256
base_H = np.array([[2.9322348, 0.0155424, 154.69591],
                   [0.01431386, 2.9198198, 420.12244],
                   [2.389e-05, 1.701e-05, 0.99271709]], np.float32)
H_base_inv = np.linalg.inv(base_H)

while True:
    tx = cv2.getTrackbarPos("tx", "focus") #- 500
    ty = cv2.getTrackbarPos("ty", "focus") #- 500
    s = cv2.getTrackbarPos("scale", "focus") / 100.0
    r = np.deg2rad(cv2.getTrackbarPos("rot", "focus"))

    # Build adjustment matrix
    cos_r, sin_r = np.cos(r), np.sin(r)
    adj = np.array([
        [s*cos_r, -s*sin_r, -tx],
        [s*sin_r,  s*cos_r, -ty],
        [0, 0, 1]
    ], np.float32)

    H = adj  # apply adjustment
    corners = get_warp_corners(H, width, height)
    vis = draw_focus_region(img, corners)

    cv2.imshow("focus", vis)
    key = cv2.waitKey(16) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyWindow("focus")
print(H)

corners = get_warp_corners(H, width, height)
vis = draw_focus_region(img, corners)
cv2.imshow("focus", vis)
cv2.waitKey(0)
cv2.imshow("warped", cv2.warpPerspective(img, H, (width, height), flags=cv2.INTER_NEAREST))
cv2.waitKey(0)
cv2.destroyAllWindows()