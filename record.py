# record.py
import os
import subprocess
import time
from datetime import datetime

rec_folder = 'tmp'
recordings_folder = 'upload'

if not os.path.exists(rec_folder):
    os.makedirs(rec_folder)

if not os.path.exists(recordings_folder):
    os.makedirs(recordings_folder)

clip_duration = 12 * 60 * 60  # Duration of the video clip in seconds
camera_name = "OBS Virtual Camera"

def start_recording():
    while True:
        curr_datetime = datetime.now().strftime('%Y %m %d')
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-f",
            "dshow",
            "-t",
            str(clip_duration),
            "-i",
            f"video={camera_name}",
            os.path.join(rec_folder, f"{curr_datetime}.mkv")
        ]

        print("Running command:", " ".join(command))
        subprocess.run(command)

        recorded_file = os.path.join(rec_folder, f"{curr_datetime}.mkv")
        new_file_path = os.path.join(recordings_folder, f"{curr_datetime}.mkv")
        os.rename(recorded_file, new_file_path)
        print(f"Moved recorded file to {new_file_path}")

        time.sleep(1)  # Optional delay before the next recording

if __name__ == "__main__":
    start_recording()
