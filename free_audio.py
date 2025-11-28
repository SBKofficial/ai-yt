import json
import edge_tts
import asyncio
import os
from gtts import gTTS # Backup engine

# Remove special characters that confuse audio engines
def clean_text_for_audio(text):
    return text.replace('*', '').replace('#', '').replace('"', '')

async def generate_voiceover(json_filename):
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    # Clean up the script text
    full_script = " ".join([seg['text'] for seg in data['segments']])
    full_script = clean_text_for_audio(full_script)
    
    folder_name = json_filename.replace(".json", "")
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    subtitle_path = f"assets/{folder_name}/subtitles.vtt"
    
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    print(f"🗣️ Generating Audio ({len(full_script)} chars)...")

    # --- PLAN A: EDGE TTS (Cinematic Voice) ---
    try:
        print("   🎙️ Trying Edge-TTS (Cinematic)...")
        communicate = edge_tts.Communicate(full_script, "en-US-ChristopherNeural")
        submaker = edge_tts.SubMaker()
        
        with open(audio_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
                    
        # Save subtitles if Edge worked
        with open(subtitle_path, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
            
        print("   ✅ Edge-TTS Success!")

    except Exception as e:
        # --- PLAN B: GOOGLE TTS (Reliable Fallback) ---
        print(f"   ⚠️ Edge-TTS Failed ({e}). Switching to Backup...")
        print("   🎙️ Trying Google TTS (Reliable)...")
        
        try:
            # Generate standard audio
            tts = gTTS(text=full_script, lang='en', slow=False)
            tts.save(audio_path)
            
            # Google doesn't give timestamps, so we delete the subtitle file 
            # (The Editor script knows to skip text if this file is missing)
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)
                
            print("   ✅ Google TTS Success!")
            
        except Exception as e2:
            print(f"   ❌ ALL AUDIO ENGINES FAILED: {e2}")
            raise e2

    # Verification
    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
        data['audio_path'] = audio_path
        # Only save subtitle path if it actually exists
        if os.path.exists(subtitle_path):
            data['subtitle_path'] = subtitle_path
        
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        raise Exception("Audio file is empty or missing.")

if __name__ == "__main__":
    # Test
    pass
