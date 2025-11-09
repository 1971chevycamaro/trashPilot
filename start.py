import subprocess
import signal
import time

scripts = [
    "webcam_server_robust.py",
    "myui.py",
    "display_steering3.py",
    "mycarcontroller.py",
    "mymodeld3.py"
    
]

procs = []
for s in scripts:
    procs.append(subprocess.Popen(["python", s]))
    time.sleep(0.5)  # Sleep 2 seconds before starting next process

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
    for p in procs:
        p.terminate()
        p.wait()
