import asyncio
import os
import sys
import json
import random
from concurrent.futures import ThreadPoolExecutor

# Google & YouTube Imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Import your helper scripts
from free_creator import generate_free_script, get_viral_topic
from free_artist import download_free_images
from free_audio import generate_voiceover
from editor import create_video

def upload_to_youtube(video_path, title, topic):
    print("🚀 Uploading to YouTube...")
    
    # 1. Load Token from GitHub Secrets
    token_json = os.environ.get('YOUTUBE_TOKEN')
    if not token_json:
        print("❌ Error: No YOUTUBE_TOKEN found in Secrets! Video saved but not uploaded.")
        return

    try:
        # 2. Connect to YouTube
        creds = Credentials.from_authorized_user_info(json.loads(token_json))
        youtube = build('youtube', 'v3', credentials=creds)
        
        # 3. Metadata (Title, Description, Tags)
        description_text = (
            f"The truth about {topic}.\n\n"
            "Echoes of Reality explores the glitches in our world, the paradoxes that break logic, "
            "and the dark corners of history.\n\n"
            "Subscribe for daily mysteries.\n"
            "#shorts #mystery #documentary #facts #scifi"
        )

        request_body = {
            'snippet': {
                'title': f"{title} #Shorts",
                'description': description_text,
                'tags': ['shorts', 'mystery', 'facts', 'dark history', 'paradox'],
                'categoryId': '27' # Category 27 is Education
            },
            'status': {
                # CHANGE THIS TO 'private' IF YOU WANT TO REVIEW BEFORE POSTING
                'privacyStatus': 'public', 
                'selfDeclaredMadeForKids': False
            }
        }
        
        # 4. Upload
        print(f"   📤 Pushing file: {video_path}")
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )
        
        response = request.execute()
        print(f"✅ UPLOAD COMPLETE! Video is live.")
        print(f"   🔗 URL: https://youtube.com/shorts/{response['id']}")

    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        # We don't exit here, so we can still see the artifact if needed

def run_once():
    print("☁️ ECHOES OF REALITY: CLOUD BOT STARTED ☁️")
    
    # 1. BRAIN: Generate Script
    topic = get_viral_topic()
    json_filename = generate_free_script(topic)
    if not json_filename: 
        print("❌ Script generation failed.")
        sys.exit(1)
    
    # Load title for YouTube
    with open(json_filename, 'r') as f:
        data = json.load(f)
        # Use the generated title, or fallback to the topic name
        video_title = data.get('title', topic)

    # 2. ASSETS: Sequential Mode (Safest for Cloud)
    print("\n⚡ Generating Assets...")
    
    # A. Audio First (Critical)
    try:
        asyncio.run(generate_voiceover(json_filename))
    except Exception as e:
        print(f"❌ Audio Failed. Stopping run. Error: {e}")
        sys.exit(1)

    # B. Images Second
    download_free_images(json_filename)

    # 3. EDITOR: Render Video
    print("\n🎬 Rendering Video...")
    try:
        create_video(json_filename)
        final_file = json_filename.replace('.json', '_FINAL.mp4')
    except Exception as e:
        print(f"❌ Editor Failed. Error: {e}")
        sys.exit(1)
    
    # 4. UPLOADER: Push to YouTube
    if os.path.exists(final_file):
        upload_to_youtube(final_file, video_title, topic)
    else:
        print("❌ Video file missing. Cannot upload.")
        sys.exit(1)

if __name__ == "__main__":
    run_once()
