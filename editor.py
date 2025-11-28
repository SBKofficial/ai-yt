import json
import os
import random

# --- FIX FOR "ANTIALIAS" ERROR ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ---------------------------------

from moviepy.editor import *

def create_video(json_filename):
    # 1. Load Data
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {json_filename} not found.")
        return
        
    folder_name = json_filename.replace(".json", "")
    
    # Construct paths
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    asset_dir = f"assets/{folder_name}"
    
    # Get images
    try:
        image_files = [f for f in os.listdir(asset_dir) if f.endswith('.jpg') or f.endswith('.png')]
        # Sort by number to ensure story order
        image_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        image_paths = [os.path.join(asset_dir, f) for f in image_files]
    except Exception as e:
        print(f"❌ Error finding images: {e}")
        return
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file missing at {audio_path}")
        return

    print(f"🎬 Assembling video: {folder_name}")

    # 2. Setup Audio
    audio_clip = AudioFileClip(audio_path)
    # Add a 1-second buffer so the video doesn't cut off abruptly
    total_duration = audio_clip.duration + 1
    duration_per_image = total_duration / len(image_paths)

    clips = []
    
    # 3. Create Clips
    for img_path in image_paths:
        # Create Image Clip
        clip = ImageClip(img_path).set_duration(duration_per_image)
        
        # Resize to fit vertical screen (height=1280)
        clip = clip.resize(height=1280) 
        clip = clip.set_position("center")
        
        # Random Slow Zoom Effect
        zoom_mode = random.choice(['in', 'out'])
        
        if zoom_mode == 'in':
            # Zoom In: Scale 1.0 -> 1.04
            clip = clip.resize(lambda t: 1 + 0.04 * t)
        else:
            # Zoom Out: Scale 1.10 -> 1.06
            clip = clip.resize(lambda t: 1.10 - 0.04 * t)
            
        clips.append(clip)

    # 4. Concatenate
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    # 5. Export
    output_filename = f"{folder_name}_FINAL.mp4"
    
    print("   ⚙️ Turbo Rendering video...")
    
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=8,             # Use all CPU cores
        preset="ultrafast"     # <--- THE MAGIC SETTING
    )
    
    print(f"✅ SUCCESS! Video saved as: {output_filename}")

if __name__ == "__main__":
    create_video("The_Dead_Internet_Theory.json")
