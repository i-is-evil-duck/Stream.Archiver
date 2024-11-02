import os
import time
import httplib2
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from googleapiclient.http import MediaFileUpload

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
UPLOAD_DIR = "C:\\Users\\Ducky\\Documents\\visualstudio\\api\\recordings"
VIDEO_LINKS_FILE = "video_links.json"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Load existing video links or create a new list
if os.path.exists(VIDEO_LINKS_FILE):
    with open(VIDEO_LINKS_FILE, 'r') as f:
        video_links = json.load(f)
else:
    video_links = []

class VideoUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.endswith(('.mp4', '.avi', '.mov', '.flv')):  # Modify for your video types
            print(f"New video detected: {file_path}")
            upload_video(file_path)

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage("youtube-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

def upload_video(file_path):
    youtube = get_authenticated_service()
    title = os.path.basename(file_path).rsplit('.', 1)[0]  # Remove file extension for title
    description = "Stream clip"
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['example', 'tag'],  # Example tags
            'categoryId': '22'  # Category ID for People & Blogs
        },
        'status': {
            'privacyStatus': 'private'  # Change as needed
        }
    }

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        video_id = response['id']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Video uploaded: {video_link}")

        # Delete the video file after successful upload
        os.remove(file_path)
        print(f"Deleted recording: {file_path}")

        # Save the video link to the JSON file
        video_links.append({"id": video_id, "link": video_link})
        with open(VIDEO_LINKS_FILE, 'w') as f:
            json.dump(video_links, f, indent=4)
        print(f"Saved video link: {video_link}")

    except HttpError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    event_handler = VideoUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_DIR, recursive=False)
    observer.start()
    print("Monitoring for new videos...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
