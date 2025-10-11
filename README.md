<p align="center">
  <img src="assets/trashpilot_logo.png" alt="TrashPilot logo" width="300">
</p>

# TrashPilot
*its total garbage*  
This is an experimental repository designed to be vastly simpler than openpilots. It exists to document my knowledge of openpilot's codebase. Inside you will find tools to test and replicate various snippets of openpilot. Features currently included are webcam capture and sharing architecture, model inference etc.

## Setup
```
git clone --recursive https://github.com/1971chevycamaro/trashPilot.git
```  
VScode should prompt you regarding setup of python environment, <u>but if not</u>, you must
make a virtual environment and `pip install -r requirements.txt` (if i keep it updated)   

for files dependent on the openpilot repo:
```git clone --recursive https://github.com/you/trashPilot.git
cd external/openpilot
git fetch --tags       # updates the list of releases
git checkout 5e3fc13751dc9b9c5d5e0991a17c672eda8bd122 # checkout a specific release cuz the models always change
git lfs install
git lfs pull
cd ../..
```
## Usage
start `webcam_server_robust.py`  
explore the results with any of the `webcam_*.py` files!  
observe your pretty face

`viewfinder.py` interactively shows the effect of a homography matrix on a provided image (may be buggy)  
`viewfinder2.py` displays the focus region of a homography matrix on a provided image then shows the result in a new window.  
the calculations performed in `viewfinder*.py` are used in openpilot's model input pipeline.

`visualization_lanes.py` shows how openpilot's model output is converted to lane lines in 3D space.
<p align="center">
  <img src="assets/Figure_1.png" alt="TrashPilot logo" width="300">
</p>

> Inspired by the ok work at [comma.ai’s openpilot](https://github.com/commaai/openpilot).