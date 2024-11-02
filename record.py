import os
import subprocess
from datetime import datetime

# Ensure the output directory exists
output_folder = 'rec'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get the current date and time to use in the filename
curr_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

# Set the duration of the video clip (in seconds)
clip_duration = 60  # 1 minute

# OBS Virtual Camera input using DirectShow
camera_name = "OBS Virtual Camera"

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
    os.path.join(output_folder, f"{curr_datetime}.mkv")  # output file
]

# Print the command for debugging purposes
print("Running command:", " ".join(command))

# Run the command
subprocess.run(command)
