from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from moviepy.editor import *
import numpy as np


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_local_server()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def initialize_upload(youtube, file):
  request = youtube.videos().insert(
    part="snippet,status",
    body={
      "snippet": {
        "title": "My video title",
        "description": "This is a description of my video",
        "tags": ["my", "video", "tags"],
        "categoryId": "22"
      },
      "status": {
        "privacyStatus": "private"
      }
    },
    media_body=MediaFileUpload(file)
  )
  response = request.execute()

  print('Video id "%s" was successfully uploaded.' % response['id'])

def make_frame(t):
    return np.zeros((480, 640, 3))

def convert_mp3_to_video(mp3_file_path, output_video_file_path):
  audio = AudioFileClip(mp3_file_path)
  video = VideoClip(make_frame, duration=audio.duration)
  video = video.set_audio(audio)
  video.write_videofile(output_video_file_path, fps=24)

if __name__ == '__main__':
  input, output = "output.mp3" , "output_test.mp4"
  # convert_mp3_to_video(input, output)
  youtube = get_authenticated_service()
  initialize_upload(youtube, 'video.mp4')