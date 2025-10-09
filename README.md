<p align="center">
  <img src="assets/trashpilot_logo.png" alt="TrashPilot logo" width="300">
</p>

# trashPilot
its total garbage  
this is an experimental repository to document my knowledge of openpilot's codebase. inside you will find tools to test and replicate various snippets of openpilot's codebase. atm it is only the webcam capture and sharing architecture.

## setup
VScode should take care of you  
make a virtual environment and `pip install -r requirements.txt` (if i keep it updated)  
## usage
start `webcam_server_robust.py`  
explore the results with any of the `webcam_*.py` files!  
observe your pretty face

`viewfinder.py` interactively shows the effect of a homography matrix on a provided image (may be buggy)  
`viewfinder2.py` displays the focus region of a homography matrix on a provided image then shows the result in a new window.  
the calculations performed in `viewfinder*.py` are used in openpilot's model input pipeline.