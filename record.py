import cv2
import os
import time
from datetime import datetime

# Specify the directory to save recordings
RECORDINGS_DIR = "C:\\Users\\Ducky\\Documents\\visualstudio\\api\\recordings"

# Create the directory if it doesn't exist
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Variable to control the recording length (in seconds)
RECORDING_LENGTH = 60  # Change this to set desired recording length

def record_clip(duration):
    # Open a connection to the webcam (default camera index is 0)
    cap = cv2.VideoCapture(0)

    # Get the frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    output_file = os.path.join(RECORDINGS_DIR, f"{timestamp}.avi")
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (frame_width, frame_height))

    print(f"Recording for {duration} seconds...")

    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to stop early
                break
        else:
            print("Failed to grab frame.")
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Recording saved to {output_file}")

if __name__ == "__main__":
    while True:  # Loop to keep recording continuously
        record_clip(RECORDING_LENGTH)
