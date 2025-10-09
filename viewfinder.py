import cv2, numpy as np

img = cv2.imread("parsedimage.png")
h, w = img.shape[:2]

# Example: base H may include scale & translation
custom_H = np.array([
    [3, 0.0, 0],
    [0.0, 3, 0],
    [0.0, 0.0, 1.0]
], dtype=np.float32)

def H_translate(tx, ty):
    return np.array([[1,0,tx],[0,1,ty],[0,0,1]], dtype=np.float32)

def H_scale_top_left(s):
    return np.array([[s,0,0],[0,s,0],[0,0,1]], dtype=np.float32)

def apply_H(H, pts_xy):
    pts = np.hstack([pts_xy.astype(np.float32), np.ones((pts_xy.shape[0],1), np.float32)])
    out = (H @ pts.T).T
    out /= out[:, [2]]
    return out[:, :2]

def draw(frame, quad):
    overlay = frame.copy()
    mask = np.zeros_like(frame, dtype=np.uint8)
    pts = quad.reshape((-1,1,2)).astype(np.int32)
    cv2.fillPoly(mask, [pts], (255,255,255))
    dim = cv2.addWeighted(frame, 0.25, np.zeros_like(frame), 0.75, 0)
    dim[mask[:,:,0] > 0] = overlay[mask[:,:,0] > 0]
    cv2.polylines(dim, [pts], True, (0,255,0), 4)
    return dim

# --- UI ---
cv2.namedWindow("view", cv2.WINDOW_NORMAL)

# Translation sliders: 0..1000 with 500 = neutral (cancels custom_H translation)
TX_RANGE = TY_RANGE = 1000
NEUTRAL_TX = NEUTRAL_TY = 500

# Scale slider: 0..400 with 100 = "full image" (combined scale = 1)
SCALE_RANGE = 400
NEUTRAL_SCALE = 100

# Derive base scale from custom_H (assume isotropic; use a==d)
base_scale = float((np.linalg.norm(custom_H[:2,0]) + np.linalg.norm(custom_H[:2,1]))/2)

# Start positions
tx_start = int(np.clip(NEUTRAL_TX + custom_H[0,2], 0, TX_RANGE))
ty_start = int(np.clip(NEUTRAL_TY + custom_H[1,2], 0, TY_RANGE))
scale_start = int(np.clip(NEUTRAL_SCALE * base_scale, 0, SCALE_RANGE))

cv2.createTrackbar("scale (0-400)", "view", scale_start, SCALE_RANGE, lambda *_: None)
cv2.createTrackbar("tx (0-1000)",  "view", tx_start,   TX_RANGE,    lambda *_: None)
cv2.createTrackbar("ty (0-1000)",  "view", ty_start,   TY_RANGE,    lambda *_: None)

view_rect = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32)

while True:
    s_slider = cv2.getTrackbarPos("scale (0-400)", "view")   # e.g. 157
    sx = cv2.getTrackbarPos("tx (0-1000)", "view")
    sy = cv2.getTrackbarPos("ty (0-1000)", "view")

    # Translation neutral: (500,500) cancels custom_H translation
    dx = float(sx - (NEUTRAL_TX + custom_H[0,2]))
    dy = float(sy - (NEUTRAL_TY + custom_H[1,2]))

    # --- KEY MAPPING (correct): ---
    # s_adj = s_slider / (NEUTRAL_SCALE * base_scale)
    # H_total = T(dx,dy) @ custom_H @ S_top_left(s_adj)
    # => Combined scale = base_scale * s_adj = s_slider / NEUTRAL_SCALE
    #    so slider==100 -> combined==1 (full image), independent of base_scale.
    s_adj = (s_slider / max(1, NEUTRAL_SCALE * base_scale))
    H_total = H_translate(dx, dy) @ custom_H @ H_scale_top_left(s_adj)

    quad = apply_H(H_total, view_rect)
    frame = draw(img, quad)
    cv2.imshow("view", frame)
    if cv2.waitKey(16) == 27: break

cv2.destroyAllWindows()