import json
import os
import random
import textwrap
import math

# Fix for PIL Image Antialias
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import *
import moviepy.audio.fx.all as afx 
import moviepy.video.fx.all as vfx

def create_video(json_filename):
    print("   🔹 Step 1: Loading Data...")
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
            # Fallback if title is missing
            video_title = data.get('title', json_filename.replace('.json', '').replace('_', ' '))
            segments = data.get('segments', [])
    except FileNotFoundError:
        print(f"❌ Error: File {json_filename} not found.")
        return

    folder_name = json_filename.replace(".json", "")
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    asset_dir = f"assets/{folder_name}"
    bg_music_path = "mystery_bg.mp3" 

    # 1. Load Images
    try:
        image_files = [f for f in os.listdir(asset_dir) if f.endswith('.jpg') or f.endswith('.png')]
        # Sort numerically to match segments
        image_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        image_paths = [os.path.join(asset_dir, f) for f in image_files]
        print(f"   🔹 Step 2: Found {len(image_paths)} images for {len(segments)} segments.")
    except Exception as e:
        print(f"❌ Error finding images: {e}")
        return

    if not os.path.exists(audio_path):
        print(f"❌ Audio missing at {audio_path}")
        return

    # 2. AUDIO SETUP
    print("   🔹 Step 3: Setting up Audio...")
    voice_clip = AudioFileClip(audio_path)

    # Background Music Logic
    if os.path.exists(bg_music_path):
        try:
            print("      - Adding Background Music...")
            music_clip = AudioFileClip(bg_music_path)
            # Loop music to fit voice
            music_clip = afx.audio_loop(music_clip, duration=voice_clip.duration + 2)
            music_clip = music_clip.volumex(0.12) # Slightly louder than 0.10
            music_clip = music_clip.audio_fadeout(2)
            final_audio = CompositeAudioClip([voice_clip, music_clip])
        except Exception as e:
            print(f"      ⚠️ Music Failed: {e}. Skipping music.")
            final_audio = voice_clip
    else:
        final_audio = voice_clip

    # 3. VISUAL SETUP & CAPTIONS
    print("   🔹 Step 4: Processing Images & Captions...")
    
    # Calculate timing
    total_duration = voice_clip.duration
    # Use the count of images to determine duration per clip
    if len(image_paths) > 0:
        duration_per_image = total_duration / len(image_paths)
    else:
        print("❌ No images found!")
        return

    clips = []
    
    # Loop through images and corresponding text segments
    for index, img_path in enumerate(image_paths):
        # Image Clip
        clip = ImageClip(img_path).set_duration(duration_per_image)
        clip = clip.resize(height=1280)
        
        # Center crop to 9:16 aspect ratio (720x1280)
        if clip.w > 720:
            clip = clip.crop(x1=clip.w/2 - 360, width=720)
            
        clip = clip.set_position("center")

        # --- Dynamic Zoom ---
        if index == 0:
            clip = clip.resize(lambda t: 1 + 0.1 * t) # Aggressive zoom for hook
        else:
            zoom_mode = random.choice(['in', 'out'])
            if zoom_mode == 'in':
                clip = clip.resize(lambda t: 1 + 0.04 * t)
            else:
                clip = clip.resize(lambda t: 1.10 - 0.04 * t)

        # Darken image slightly to make text pop
        clip = clip.fx(vfx.colorx, 0.8)

        # --- CAPTION LOGIC ---
        # Get text for this segment. Handle index out of range safely.
        segment_text = ""
        if index < len(segments):
            segment_text = segments[index].get('text', '')
        
        # Wrap text so it doesn't go off screen
        wrapper = textwrap.TextWrapper(width=20) 
        word_list = wrapper.wrap(text=segment_text) 
        caption_str = "\n".join(word_list)

        if caption_str.strip():
            # Yellow text with black outline (Classic Shorts Style)
            txt_clip = TextClip(
                caption_str,
                fontsize=55,
                color='yellow',
                font='DejaVu-Sans-Bold', # Ensure you have a bold font on your system
                stroke_color='black',
                stroke_width=3,
                method='caption',
                align='center',
                size=(680, None) # Limit width to 680px
            )
            # Position text in the center-bottom
            txt_clip = txt_clip.set_position(('center', 800)).set_duration(duration_per_image)
            
            # Combine Image + Text
            video_segment = CompositeVideoClip([clip, txt_clip])
        else:
            video_segment = clip

        clips.append(video_segment)

    # Concatenate all segments
    base_video = concatenate_videoclips(clips, method="compose")
    base_video = base_video.set_audio(final_audio)

    # 4. BIG TITLE OVERLAY (Only for the first 3 seconds)
    print("   🔹 Step 5: Adding Title Hook...")
    try:
        wrapped_title = "\n".join(textwrap.wrap(video_title.upper(), width=15))
        
        title_clip = TextClip(
            wrapped_title,
            fontsize=85,
            color='white',
            font='DejaVu-Sans-Bold',
            stroke_color='black',
            stroke_width=6,
            method='caption',
            align='center',
            size=(700, None)
        )
        
        # Position Title in Center
        title_clip = title_clip.set_position(('center', 'center')).set_duration(3.0)
        title_clip = title_clip.crossfadein(0.2)

        final_video = CompositeVideoClip([base_video, title_clip])

    except Exception as e:
        print(f"⚠️ Title Failed: {e}")
        final_video = base_video

    # 5. RENDER
    print("   🔹 Step 6: Rendering...")
    output_filename = f"{folder_name}_FINAL.mp4"

    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=4,
        preset="ultrafast" 
    )

    print(f"✅ VIDEO SAVED: {output_filename}")

if __name__ == "__main__":
    pass
