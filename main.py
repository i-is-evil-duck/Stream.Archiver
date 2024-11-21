import os
import time
import httplib2
import http.client as httplib  # Python 3 uses http.client
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets

# Disable SSL verification (INSECURE)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Directory to monitor
UPLOAD_DIR = r"C:\api\upload"
CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_UPLOAD_SCOPE = "http://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

MISSING_CLIENT_SECRETS_MESSAGE = f"""
WARNING: Please configure OAuth 2.0.

To make this script run, you need to populate the client_secrets.json file found at:
{os.path.abspath(CLIENT_SECRETS_FILE)}

Visit http://console.cloud.google.com/ to configure the project.
"""

def get_authenticated_service():
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE
    )
    storage = Storage("oauth2.json")
    credentials = storage.get()

    if not credentials or credentials.invalid:
        credentials = run_flow(flow, storage)

    # Create an HTTP client with SSL verification disabled
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    authorized_http = credentials.authorize(http)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=authorized_http)


def upload_video(youtube, file_path):
    title = os.path.basename(file_path)
    description = f"Uploaded automatically by script. Filename: {title}"
    tags = ["automation", "upload"]
    category = "22"  # People & Blogs

    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus="private"
        )
    )

    print(f"Uploading file: {file_path}")
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    resumable_upload(request)

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    start_time = time.time()
    last_update_time = start_time

    while response is None:
        try:
            print("Uploading...")

            # Log before sending the request
            print("Sending next chunk...")
            status, response = insert_request.next_chunk()
            
            # Log if we receive a status update
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%...")
                print(f"Request sent, awaiting response...")

            # Log if the upload is complete
            if response:
                print("Response received.")
                if "id" in response:
                    print(f"Video ID '{response['id']}' uploaded successfully.")
                else:
                    print(f"Unexpected response: {response}")

        except HttpError as e:
            # Log HTTP errors
            if e.resp.status in [500, 502, 503, 504]:
                error = f"Retriable HTTP error {e.resp.status}:\n{e.content}"
            else:
                raise
        except (httplib.HTTPException, IOError) as e:
            # Log retriable errors
            error = f"Retriable error occurred: {str(e)}"
        except Exception as e:
            # Catch any other unexpected issues
            print(f"An unexpected error occurred: {str(e)}")
            break

        if error:
            print(error)
            retry += 1
            if retry > 10:
                print("Max retries reached. Exiting.")
                return
            sleep_time = 2 ** retry
            print(f"Sleeping {sleep_time} seconds before retrying...")
            time.sleep(sleep_time)

    print(f"Upload completed in {time.time() - start_time:.2f} seconds.")

def monitor_directory(youtube):
    uploaded_files = set()
    while True:
        files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".mkv")]
        new_files = [f for f in files if f not in uploaded_files]

        for file_name in new_files:
            file_path = os.path.join(UPLOAD_DIR, file_name)
            try:
                upload_video(youtube, file_path)
                uploaded_files.add(file_name)
                os.remove(file_path)  # Delete after upload
            except Exception as e:
                print(f"Error uploading {file_name}: {e}")

        time.sleep(10)  # Poll every 10 seconds

if __name__ == "__main__":
    youtube_service = get_authenticated_service()
    print(f"Monitoring directory: {UPLOAD_DIR}")
    monitor_directory(youtube_service)
