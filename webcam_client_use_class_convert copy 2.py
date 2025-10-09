import numpy as np
import cv2
import time
from class_webcam_client import FrameClient
# from conversions import RGB2YUV
import numpy as np

def RGBtoVISIONFMT(rgb: np.ndarray) -> np.ndarray:
    """
    Convert an RGB image of any size to OpenPilot's visionfmt (1x6x128x256).
    Crops to correct aspect ratio before resizing to avoid stretching.
    
    Args:
        rgb (np.ndarray): Input image, shape (H, W, 3), dtype uint8.
        
    Returns:
        np.ndarray: Output in shape (1, 6, 128, 256), dtype uint8.
    """
    H, W = rgb.shape[:2]
    target_h, target_w = 256, 512
    target_aspect = target_w / target_h

    # --- Crop to maintain aspect ratio ---
    in_aspect = W / H
    if in_aspect > target_aspect:  
        # too wide → crop horizontally
        new_w = int(H * target_aspect)
        start = (W - new_w) // 2
        rgb = rgb[:, start:start+new_w]
    else:  
        # too tall → crop vertically
        new_h = int(W / target_aspect)
        start = (H - new_h) // 2
        rgb = rgb[start:start+new_h, :]

    # --- Resize to 256x512 using nearest-neighbor ---
    Hc, Wc = rgb.shape[:2]
    y_idx = (np.linspace(0, Hc - 1, target_h)).astype(np.int32)
    x_idx = (np.linspace(0, Wc - 1, target_w)).astype(np.int32)
    resized = rgb[y_idx][:, x_idx]

    # --- RGB → YUV420 ---
    R, G, B = resized[...,0], resized[...,1], resized[...,2]
    Y = (0.257 * R + 0.504 * G + 0.098 * B + 16).astype(np.uint8)
    U = (-0.148 * R - 0.291 * G + 0.439 * B + 128).astype(np.uint8)
    V = (0.439 * R - 0.368 * G - 0.071 * B + 128).astype(np.uint8)

    # --- Subsample U, V to half resolution (128x256) ---
    U_ds = U.reshape(128, 2, 256, 2).mean(axis=(1,3)).astype(np.uint8)
    V_ds = V.reshape(128, 2, 256, 2).mean(axis=(1,3)).astype(np.uint8)

    # --- Pack into 6 channels ---
    out = np.empty((6, 128, 256), dtype=np.uint8)
    out[0] = Y[0::2, 0::2]
    out[2] = Y[0::2, 1::2]
    out[1] = Y[1::2, 0::2]
    out[3] = Y[1::2, 1::2]
    out[4] = U_ds
    out[5] = V_ds

    return out[None, ...]   # (1, 6, 128, 256)

def rgb_to_visionfmt_bilinear(rgb: np.ndarray) -> np.ndarray:
    """Same as NN but bilinear resize using cv2 (still needed for speed baseline)."""
    H, W = rgb.shape[:2]
    target_h, target_w = 256, 512
    target_aspect = target_w / target_h

    # Crop
    in_aspect = W / H
    if in_aspect > target_aspect:
        new_w = int(H * target_aspect)
        start = (W - new_w) // 2
        rgb = rgb[:, start:start+new_w]
    else:
        new_h = int(W / target_aspect)
        start = (H - new_h) // 2
        rgb = rgb[start:start+new_h, :]

    # Bilinear resize
    resized = cv2.resize(rgb, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

    # RGB → YUV420
    R, G, B = resized[...,0], resized[...,1], resized[...,2]
    Y = (0.257 * R + 0.504 * G + 0.098 * B + 16).astype(np.uint8)
    U = (-0.148 * R - 0.291 * G + 0.439 * B + 128).astype(np.uint8)
    V = (0.439 * R - 0.368 * G - 0.071 * B + 128).astype(np.uint8)

    # Subsample U, V
    U_ds = U.reshape(128, 2, 256, 2).mean(axis=(1,3)).astype(np.uint8)
    V_ds = V.reshape(128, 2, 256, 2).mean(axis=(1,3)).astype(np.uint8)

    # Pack
    out = np.empty((6, 128, 256), dtype=np.uint8)
    out[0] = Y[0::2, 0::2]
    out[1] = Y[0::2, 1::2]
    out[2] = Y[1::2, 0::2]
    out[3] = Y[1::2, 1::2]
    out[4] = U_ds
    out[5] = V_ds

    return out[None, ...]


client = FrameClient()  # attach to shared memory
frame = client.getFrame()
running = True

while running:

    # print(frame.shape)
    VISIONFMT = rgb_to_visionfmt_bilinear(frame)
    # np.save("visionfmt.npy", np.concatenate([VISIONFMT, VISIONFMT], axis=1))
    cv2.imshow("Frame Y", VISIONFMT[0][0])
    if cv2.waitKey(1) & 0xFF == ord('q'):
        client.close()
        running = False
    time.sleep(0.01)
client.close()
cv2.destroyAllWindows()

