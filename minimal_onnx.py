import onnxruntime as ort
import numpy as np

# Load ONNX model
session = ort.InferenceSession("external/openpilot/selfdrive/modeld/models/driving_vision.onnx")

# Get input names
input_names = [inp.name for inp in session.get_inputs()]
print("Model input names:", input_names)

# Create dummy inputs with correct shape and dtype
img = np.random.rand(1, 12, 128, 256).astype(np.uint8)
big_img = np.random.rand(1, 12, 128, 256).astype(np.uint8)

# Prepare inputs dictionary (match input names)
inputs = {
    input_names[0]: img,
    input_names[1]: big_img
}

# Run the model
outputs = session.run(None, inputs)

# Show output
# [0][0][117:629] hidden_state slice
print("Model outputs:", outputs[0][0][117:629])
print("Output shapes:", [out.shape for out in outputs])
