import asyncio
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor

# Google & YouTube Imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from free_creator import generate_free_script, get_viral_topic
from free_artist import download_free_images
from free_audio import generate_voiceover
from editor import create_video

# ... (Keep upload_to_youtube function as is) ...

def run_once():
    print("☁️ ECHOES OF REALITY: CLOUD BOT STARTED ☁️")
    
    # 1. Brain
    topic = get_viral_topic()
    json_filename = generate_free_script(topic)
    if not json_filename: sys.exit(1)
    
    # Load title
    with open(json_filename, 'r') as f:
        data = json.load(f)
        video_title = data.get('title', topic)

    # 2. Assets (SEQUENTIAL MODE FOR STABILITY)
    print("⚡ Generating Assets...")
    
    # A. Audio First (Critical)
    try:
        asyncio.run(generate_voiceover(json_filename))
    except Exception as e:
        print(f"❌ Audio Failed. Stopping run. Error: {e}")
        sys.exit(1)

    # B. Images Second (Parallel Download is fine here)
    download_free_images(json_filename)

    # 3. Editor
    try:
        create_video(json_filename)
        final_file = json_filename.replace('.json', '_FINAL.mp4')
    except Exception as e:
        print(f"❌ Editor Failed. Error: {e}")
        sys.exit(1)
    
    # 4. Upload
    if os.path.exists(final_file):
        # Pass the 'topic' variable as the 3rd argument
        upload_to_youtube(final_file, video_title, topic)
    else:
        print("❌ Video file missing. Cannot upload.")
        sys.exit(1)

if __name__ == "__main__":
    run_once()
