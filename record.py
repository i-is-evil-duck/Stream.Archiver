import os
import subprocess
import time
from datetime import datetime

# Ensure the output directories exist
rec_folder = 'rec'
recordings_folder = 'recordings'

if not os.path.exists(rec_folder):
    os.makedirs(rec_folder)

if not os.path.exists(recordings_folder):
    os.makedirs(recordings_folder)

# Set the duration of the video clip (in seconds)
clip_duration = 60  # 1 minute

# OBS Virtual Camera input using DirectShow
camera_name = "OBS Virtual Camera"

while True:
    # Get the current date and time to use in the filename
    curr_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

    # FFMPEG command
    command = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f",
        "dshow",
        "-t",
        str(clip_duration),  # duration of the recording in seconds
        "-i",
        f"video={camera_name}",  # input video device
        os.path.join(rec_folder, f"CAM001_{curr_datetime}.mkv")  # output file
    ]

    # Print the command for debugging purposes
    print("Running command:", " ".join(command))

    # Run the command and wait for it to finish
    subprocess.run(command)

    # Move the recorded file to the recordings folder
    recorded_file = os.path.join(rec_folder, f"CAM001_{curr_datetime}.mkv")
    new_file_path = os.path.join(recordings_folder, f"CAM001_{curr_datetime}.mkv")

    # Move the file
    os.rename(recorded_file, new_file_path)
    print(f"Moved recorded file to {new_file_path}")

    # Optionally, you can add a delay before starting the next recording
    time.sleep(1)  # 1 second delay before the next recording starts
