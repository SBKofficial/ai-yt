import asyncio
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

from creator import generate_free_script, get_viral_topic
from free_artist import download_free_images
from free_audio import generate_voiceover
from editor import create_video

def run_once():
    print("☁️ RUNNING ON GITHUB CLOUD ☁️")
    
    # 1. Get Topic
    topic = get_viral_topic()
    
    # 2. Generate
    json_filename = generate_free_script(topic)
    if not json_filename: sys.exit(1)

    # 3. Download Assets (Parallel is safe on GitHub's fast internet!)
    def run_audio():
        asyncio.run(generate_voiceover(json_filename))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(download_free_images, json_filename)
        executor.submit(run_audio)

    # 4. Render
    create_video(json_filename)
    
    # Print the final filename so GitHub can find it
    final_file = json_filename.replace('.json', '_FINAL.mp4')
    print(f"::set-output name=video_file::{final_file}")

if __name__ == "__main__":
    run_once()
