import os
import shutil
import schedule
import time
from datetime import datetime

# Define source and destination directories
source_dir = r'C:\path\to\videos'  # Update this path to the actual location
destination_dir = r'C:\api\upload'

def move_files():
    """Moves all .mkv files from source_dir to destination_dir."""
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
    """Deletes all files in destination_dir that are not in use."""
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

# Schedule the tasks
schedule.every().day.at("11:00").do(move_files)
schedule.every().day.at("11:30").do(delete_files)

print("Scheduled tasks started. Waiting for the scheduled times...")

# Keep the script running to check schedule
while True:
    try:
        schedule.run_pending()
    except Exception as e:
        print(f"Error during scheduled task: {e}")
    time.sleep(1)
