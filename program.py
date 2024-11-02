import subprocess
import time
import datetime
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Configuration
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
STREAM_URL = "rtmp://your_stream_url_here"
VIDEO_DIR = "./videos"
RECORD_DURATION = 24 * 3600  # 24 hours in seconds

# Ensure video directory exists
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# Authenticate with YouTube API
def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

# Function to record the stream
def record_stream():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(VIDEO_DIR, f"{timestamp}.mp4")
    command = [
        "ffmpeg", "-y", "-i", STREAM_URL, "-t", str(RECORD_DURATION),
        "-c", "copy", video_path
    ]
    subprocess.run(command)
    return video_path

# Function to upload video to YouTube
def upload_video(file_path, title, description, category="22", keywords="stream,24/7", privacy_status="private"):
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": keywords.split(","),
            "categoryId": category,
        },
        "status": {
            "privacyStatus": privacy_status,  # Set to "private" to ensure it is uploaded privately
        }
    }
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    # Handle upload and response
    response = None
    retry_count = 0
    while response is None:
        try:
            print(f"Uploading {file_path} to YouTube...")
            _, response = insert_request.next_chunk()
            if "id" in response:
                print(f"Video uploaded successfully with ID: {response['id']}")
            else:
                print("Failed to get video ID after upload.")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                print(f"Retriable error: {e}")
                retry_count += 1
                if retry_count > 10:
                    print("Max retries reached. Upload failed.")
                    break
                time.sleep(2 ** retry_count)
            else:
                print(f"HTTP error: {e}")
                break
    return response

# Main loop to record and upload in 24-hour segments
if __name__ == "__main__":
    while True:
        # Step 1: Record a 24-hour segment
        print("Starting new 24-hour recording...")
        video_file = record_stream()
        print(f"Recorded 24-hour segment to {video_file}")

        # Step 2: Prepare metadata
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"24/7 Stream Recording - {timestamp}"
        description = f"This video is a 24-hour archive of the live stream recorded on {timestamp}."

        # Step 3: Upload to YouTube with private privacy status
        upload_video(video_file, title, description)

        # Step 4: Remove the uploaded file to save space
        os.remove(video_file)
        print(f"Removed local file {video_file}")
