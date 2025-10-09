import cv2
import numpy as np

def main():
    # Open default webcam (index 0)
    cap = cv2.VideoCapture(1)  # CAP_DSHOW reduces overhead on Windows

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # frame is already a NumPy array (H x W x 3, dtype=uint8)
        frame_np: np.ndarray = frame  

        # Display the frame
        cv2.imshow("Webcam", frame_np)

        # Quit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
