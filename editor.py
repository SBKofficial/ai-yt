import json
import os
import random
import re

# --- FIX FOR PIL ERROR ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# -------------------------

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

def time_to_seconds(time_str):
    # Converts "00:00:01.500" to 1.5
    h, m, s = time_str.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def parse_vtt(vtt_path):
    # Reads the VTT file and returns list of (start, end, text)
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find timestamps and text
    # Pattern: 00:00:00.000 --> 00:00:03.000
    pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\n\d|\Z)', re.DOTALL)
    matches = pattern.findall(content)
    
    subs = []
    for start_str, end_str, text in matches:
        start = time_to_seconds(start_str)
        end = time_to_seconds(end_str)
        subs.append(((start, end), text.strip()))
    return subs

def create_video(json_filename):
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
    except:
        print("❌ JSON not found")
        return
        
    folder_name = json_filename.replace(".json", "")
    asset_dir = f"assets/{folder_name}"
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    subtitle_path = f"assets/{folder_name}/subtitles.vtt" # NEW
    
    # Load Images
    image_files = [f for f in os.listdir(asset_dir) if f.endswith('.jpg') or f.endswith('.png')]
    image_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    image_paths = [os.path.join(asset_dir, f) for f in image_files]

    print(f"🎬 Assembling with Dynamic Text: {folder_name}")

    # 1. Base Video (Images + Zoom)
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration + 1
    duration_per_image = total_duration / len(image_paths)

    clips = []
    for img_path in image_paths:
        clip = ImageClip(img_path).set_duration(duration_per_image)
        clip = clip.resize(height=1280).set_position("center")
        
        zoom = random.choice(['in', 'out'])
        if zoom == 'in': clip = clip.resize(lambda t: 1 + 0.04 * t)
        else: clip = clip.resize(lambda t: 1.10 - 0.04 * t)
        clips.append(clip)

    base_video = concatenate_videoclips(clips, method="compose")
    base_video = base_video.set_audio(audio_clip)

    # 2. Add Dynamic Subtitles
    print("   📝 Burning Captions...")
    
    if os.path.exists(subtitle_path):
        # Generator function for TextClip
        # We use a bold yellow font for that "Viral" look
        generator = lambda txt: TextClip(
            txt, 
            font='Arial-Bold', 
            fontsize=80, 
            color='yellow', 
            stroke_color='black', 
            stroke_width=3, 
            method='caption', 
            size=(700, None)
        )
        
        # Parse VTT manually to avoid MoviePy bugs
        subs_data = parse_vtt(subtitle_path)
        sub_clips = []
        
        for (start, end), text in subs_data:
            txt_clip = generator(text)
            txt_clip = txt_clip.set_start(start).set_duration(end - start)
            txt_clip = txt_clip.set_position(('center', 900)) # Bottom-Center
            sub_clips.append(txt_clip)
            
        # Combine everything
        final_video = CompositeVideoClip([base_video, *sub_clips])
    else:
        print("   ⚠️ No subtitles found. Skipping text.")
        final_video = base_video

    # 3. Export
    output_filename = f"{folder_name}_FINAL.mp4"
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    print(f"✅ DONE: {output_filename}")

if __name__ == "__main__":
    create_video("The_Glitch_in_the_Familiar.json")
