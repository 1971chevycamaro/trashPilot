# VisionIPC and Model Inputs Overview

![VisionIPC Client](visionipc.png)

`visionipc.png` is a sample image showing the **VisionIPC client** from **openpilot**.  
Use it as a reference when making your edits!

---

### `img*.png`
The files named `img*.png` represent the **parsed RGB raw inputs** to the openpilot model.  
> ⚠️ Note: The *actual* model inputs are in a special **YV12 format**, not RGB.

`extracted_big_img.npy` & `extracted_img.npy` are the saved numpy inputs to the vision model. You can view them with "Numpy Image Preview" a VScode extension
