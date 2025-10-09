import numpy as np
import cv2
import ctypes

def resize_and_crop(frame, target_w=512, target_h=256):
    h, w = frame.shape[:2]
    target_aspect = target_w / target_h
    aspect = w / h

    if aspect > target_aspect:
        # Too wide → match height, crop width
        new_h = target_h
        new_w = int(aspect * target_h)
    else:
        # Too tall → match width, crop height
        new_w = target_w
        new_h = int(target_w / aspect)

    # Resize with preserved aspect ratio
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Center crop
    start_x = (new_w - target_w) // 2
    start_y = (new_h - target_h) // 2
    return resized[start_y:start_y+target_h, start_x:start_x+target_w]

def resize_and_crop2(frame, target_w=512, target_h=256, offset_x=0, offset_y=0):
    h, w = frame.shape[:2]
    target_aspect = target_w / target_h
    aspect = w / h

    if aspect > target_aspect:
        # Too wide → match height, crop width
        new_h = target_h
        new_w = int(aspect * target_h)
    else:
        # Too tall → match width, crop height
        new_w = target_w
        new_h = int(target_w / aspect)

    # Resize with preserved aspect ratio
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Compute crop origin, apply offsets (positive = shift right/down)
    start_x = (new_w - target_w) // 2 + offset_x
    start_y = (new_h - target_h) // 2 + offset_y

    # Clamp crop bounds
    start_x = max(0, min(start_x, new_w - target_w))
    start_y = max(0, min(start_y, new_h - target_h))

    return resized[start_y:start_y + target_h, start_x:start_x + target_w]


def rgb_to_visionfmt_bilinear(frameBGR):
    """
    Convert an RGB frame of any size into a 6-channel VISIONFMT half.
    Resizes with preserved aspect ratio, crops to 512x256.
    """
    frame_resized = resize_and_crop2(frameBGR, 512, 256,offset_y=200)

    yuv = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2YUV)
    Y, U, V = cv2.split(yuv)

    Y0 = Y[0::2, 0::2]
    Y1 = Y[0::2, 1::2]
    Y2 = Y[1::2, 0::2]
    Y3 = Y[1::2, 1::2]

    Usub = U[0::2, 0::2]
    Vsub = V[0::2, 0::2]

    return np.expand_dims(np.stack([Y0, Y1, Y2, Y3, Usub, Vsub], axis=0), axis=0)

def RGBtoVISIONFMT_half_fast(frameBGR):
    # Resize once (3-channel)
    frame_resized = cv2.resize(frameBGR, (512, 256), interpolation=cv2.INTER_AREA)

    # Convert to YUV once
    yuv = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2YUV)
    Y, U, V = cv2.split(yuv)

    # Preallocate output
    out = np.empty((6,128,256), dtype=np.uint8)

    # Split Y into quadrants
    out[0] = Y[0::2, 0::2]
    out[1] = Y[0::2, 1::2]
    out[2] = Y[1::2, 0::2]
    out[3] = Y[1::2, 1::2]

    # Subsample U and V
    out[4] = U[0::2, 0::2]
    out[5] = V[0::2, 0::2]

    return out

# load shared library
# lib = ctypes.CDLL("./blah/libvisionfmt.so")

# # declare function prototype
# lib.RGBtoVISIONFMT_half_C.argtypes = [
#     ctypes.POINTER(ctypes.c_uint8),  # rgb input
#     ctypes.c_int,                    # width
#     ctypes.c_int,                    # height
#     ctypes.POINTER(ctypes.c_uint8)   # output buffer
# ]
# lib.RGBtoVISIONFMT_half_C.restype = None

# def RGBtoVISIONFMT_half_py(frame: np.ndarray) -> np.ndarray:
#     """
#     frame: (H,W,3) uint8 numpy array (BGR input)
#     returns: (6,128,256) uint8 numpy array
#     """
#     h, w, c = frame.shape
#     assert c == 3
#     frame = np.ascontiguousarray(frame, dtype=np.uint8)

#     out = np.empty((6,128,256), dtype=np.uint8)

#     lib.RGBtoVISIONFMT_half_C(
#         frame.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
#         w, h,
#         out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
#     )

#     return out