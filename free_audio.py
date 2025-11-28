import json
import edge_tts
import asyncio
import os

async def generate_voiceover(json_filename):
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    full_script = " ".join([seg['text'] for seg in data['segments']])
    folder_name = json_filename.replace(".json", "")
    
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    subtitle_path = f"assets/{folder_name}/subtitles.vtt"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    print(f"🗣️ Generating Audio ({len(full_script)} chars)...")

    try:
        communicate = edge_tts.Communicate(full_script, "en-US-ChristopherNeural")
        submaker = edge_tts.SubMaker()
        
        with open(audio_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
                    
        with open(subtitle_path, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
            
        # --- SAFETY CHECK ---
        # Check if file exists and is larger than 1KB
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
            raise Exception("Audio generation failed (File is empty or too small)")

        data['audio_path'] = audio_path
        data['subtitle_path'] = subtitle_path
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"✅ Audio verified: {os.path.getsize(audio_path) / 1024:.2f} KB")

    except Exception as e:
        print(f"❌ CRITICAL AUDIO ERROR: {e}")
        # Create a dummy file to prevent MoviePy crash (optional but safe)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise e # Stop the script here so we don't waste minutes

if __name__ == "__main__":
    # Test path needs to be valid
    pass
