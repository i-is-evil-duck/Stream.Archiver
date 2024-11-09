import os
import shutil
import schedule
import time
from datetime import datetime

# Define source and destination directories
source_dir = r'C:\path\to\videos'
destination_dir = r'C:\api\upload'

def move_files():
    print(f"{datetime.now()}: Moving files...")
    try:
        for filename in os.listdir(source_dir):
            if filename.endswith(".mkv"):
                source_path = os.path.join(source_dir, filename)
                destination_path = os.path.join(destination_dir, filename)
                shutil.move(source_path, destination_path)
                print(f"Moved {filename} to {destination_dir}")
    except Exception as e:
        print(f"Error moving files: {e}")

def delete_files():
    print(f"{datetime.now()}: Deleting files...")
    for filename in os.listdir(destination_dir):
        file_path = os.path.join(destination_dir, filename)
        try:
            os.remove(file_path)
            print(f"Deleted {filename}")
        except PermissionError:
            print(f"Skipping {filename} - file is in use or locked.")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

def start_clear_scheduler():
    schedule.every().day.at("11:00").do(move_files)
    schedule.every().day.at("11:30").do(delete_files)
    print("Clear scheduler tasks started. Waiting for scheduled times...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"Error in clear scheduler: {e}")
