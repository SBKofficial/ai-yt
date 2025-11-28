import asyncio
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Import your scripts
# Make sure your free_creator.py has the 'get_viral_topic' function you just wrote!
from creator import generate_free_script, get_viral_topic
from free_artist import download_free_images
from free_audio import generate_voiceover
from editor import create_video

def run_pipeline(topic):
    start_time = time.time()
    print(f"\n🚀 STARTING AUTOMATION FOR: {topic}")
    print("---------------------------------------")

    # 1. BRAIN (Scripting)
    json_filename = generate_free_script(topic)
    if not json_filename: 
        print("❌ Script failed. Skipping.")
        return

    # 2. PARALLEL GENERATION (Art + Voice)
    print("\n⚡ Generating Assets (Parallel)...")
    
    # Wrapper for async audio function
    def run_audio():
        asyncio.run(generate_voiceover(json_filename))

    # Run Artist and Audio at the same time
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(download_free_images, json_filename)
        executor.submit(run_audio)

    # 3. EDITOR (Video Assembly)
    print("\n🎬 Rendering Video...")
    create_video(json_filename)

    end_time = time.time()
    print(f"\n✅ FINISHED '{topic}' in {end_time - start_time:.1f} seconds!")
    print(f"📁 Output: {json_filename.replace('.json', '_FINAL.mp4')}")

if __name__ == "__main__":
    print("🤖 SYSTEM ONLINE: AUTO-PILOT ENGAGED")
    print("Press Ctrl+C in this terminal to stop the bot.")
    print("---------------------------------------")
    
    while True:
        try:
            # A. Get a random viral topic automatically
            topic = get_viral_topic()
            
            # B. Make the video
            run_pipeline(topic)
            
            # C. Wait before the next one
            # TESTING MODE: 60 seconds
            # PRODUCTION MODE: Change 60 to 14400 (4 hours)
            wait_time = 60 
            
            print(f"\n💤 Zzz... Sleeping for {wait_time} seconds. Next video coming up!")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"\n❌ Critical Error: {e}")
            print("Restarting loop in 30 seconds...")
            time.sleep(30)
