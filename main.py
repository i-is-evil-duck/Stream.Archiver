import os
import time
import json
import ssl
import httplib2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.http import MediaFileUpload

# Disable SSL certificate verification globally
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass  # Older Python versions don't verify HTTPS certificates by default
else:
    ssl._create_default_https_context = _create_unverified_https_context

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
UPLOAD_DIR = "upload"
LINKS_FILE = "video_links.json"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Ensure the links file exists with the correct initial structure
if not os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, 'w') as f:
        json.dump({"links": []}, f)

class VideoUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.endswith(('.mp4', '.avi', '.mkv', '.flv')):  # Modify for your video types
            print(f"New video detected: {file_path}")
            time.sleep(5)  # Wait for 5 seconds before uploading
            upload_video(file_path)

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage("youtube-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    # Disable SSL verification for httplib2.Http
    return build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http(disable_ssl_certificate_validation=True))
    )

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
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Video uploaded: {video_url}")

        # Write the new video URL to the JSON file
        write_video_link(video_url)



    except HttpError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def write_video_link(video_url):
    # Read the existing links
    with open(LINKS_FILE, 'r') as f:
        data = json.load(f)

    # Add the new video URL
    data['links'].append(video_url)

    # Write the updated links back to the file
    with open(LINKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def start_upload_monitor():
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

# Only run the monitor if the script is executed directly
if __name__ == "__main__":
    start_upload_monitor()
