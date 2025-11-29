import json
import os
import random
import textwrap

# Fix for PIL Image Antialias
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import *
import moviepy.audio.fx.all as afx
import moviepy.video.fx.all as vfx

def create_video(json_filename):
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
            # Use topic as title if missing
            video_title = data.get('title', json_filename.replace('.json', '').replace('_', ' '))
    except FileNotFoundError:
        print(f"❌ Error: File {json_filename} not found.")
        return
        
    folder_name = json_filename.replace(".json", "")
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    asset_dir = f"assets/{folder_name}"
    bg_music_path = "mystery_bg.mp3" # You must upload this file!
    
    # 1. Load Images
    try:
        image_files = [f for f in os.listdir(asset_dir) if f.endswith('.jpg') or f.endswith('.png')]
        image_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        image_paths = [os.path.join(asset_dir, f) for f in image_files]
    except Exception as e:
        print(f"❌ Error finding images: {e}")
        return
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio missing.")
        return

    print(f"🎬 ENGINEERING VIDEO: {folder_name}")

    # 2. AUDIO ENGINEERING (The "Retention" Upgrade)
    # Load Voiceover
    voice_clip = AudioFileClip(audio_path)
    
    # Speed up voice by 15% (Industry standard for retention)
    voice_clip = voice_clip.fx(vfx.speedx, 1.15)
    
    # Load Background Music
    if os.path.exists(bg_music_path):
        music_clip = AudioFileClip(bg_music_path)
        # Loop music to match voice length
        music_clip = afx.audio_loop(music_clip, duration=voice_clip.duration + 2)
        # Lower volume to 10% so voice is clear
        music_clip = music_clip.volumex(0.10)
        # Fade out music at end
        music_clip = music_clip.audio_fadeout(2)
        
        # Combine Voice + Music
        final_audio = CompositeAudioClip([voice_clip, music_clip])
    else:
        print("⚠️ Warning: 'mystery_bg.mp3' not found. Video will feel empty.")
        final_audio = voice_clip

    # 3. VISUAL ENGINEERING
    total_duration = voice_clip.duration
    duration_per_image = total_duration / len(image_paths)

    clips = []
    for img_path in image_paths:
        clip = ImageClip(img_path).set_duration(duration_per_image)
        
        # Resize to Vertical (HD)
        clip = clip.resize(height=1280)
        clip = clip.set_position("center")
        
        # A. Motion (Ken Burns)
        zoom_mode = random.choice(['in', 'out'])
        if zoom_mode == 'in':
            clip = clip.resize(lambda t: 1 + 0.04 * t)
        else:
            clip = clip.resize(lambda t: 1.10 - 0.04 * t)
        
        # B. Color Grading (The "Dark Archive" Look)
        # Decrease brightness slightly to make text pop and look moody
        clip = clip.fx(vfx.colorx, 0.9)
            
        clips.append(clip)

    base_video = concatenate_videoclips(clips, method="compose")
    base_video = base_video.set_audio(final_audio)
    
    # 4. HOOK OVERLAY (The "Stop Scroll" Text)
    # This creates a professional title card for the first 3 seconds
    print("   📝 Designing Hook Overlay...")
    
    wrapped_title = "\n".join(textwrap.wrap(video_title.upper(), width=15))
    
    # Create the text
    txt_clip = TextClip(
        wrapped_title,
        fontsize=85,
        color='white',
        font='Arial-Bold', # Standard bold font
        stroke_color='black',
        stroke_width=4,
        method='caption',
        align='center',
        size=(720, None)
    )
    
    # Animate Text: Fade In (0.5s) -> Hold -> Fade Out (0.5s)
    txt_clip = txt_clip.set_position(('center', 300))
    txt_clip = txt_clip.set_duration(3.5)
    txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
    
    # Shadow/Glow effect (black box behind text for readability)
    bg_box = ColorClip(
        size=(720, int(txt_clip.h * 1.2)),
        color=(0,0,0)
    ).set_opacity(0.4).set_duration(3.5).set_position(('center', 300))
    bg_box = bg_box.crossfadein(0.5).crossfadeout(0.5)

    # 5. RENDER
    final_video = CompositeVideoClip([base_video, bg_box, txt_clip])
    
    output_filename = f"{folder_name}_FINAL.mp4"
    print("   ⚙️ Rendering High-Fidelity Output...")
    
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )
    
    print(f"✅ ELITE VIDEO SAVED: {output_filename}")

if __name__ == "__main__":
    # Test
    create_video("The_Dead_Internet_Theory.json")
