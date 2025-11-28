import json
import edge_tts
import asyncio
import os

async def generate_voiceover(json_filename):
    # 1. Load Data
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    full_script = " ".join([seg['text'] for seg in data['segments']])
    folder_name = json_filename.replace(".json", "")
    
    # Paths
    audio_path = f"assets/{folder_name}/voiceover.mp3"
    subtitle_path = f"assets/{folder_name}/subtitles.vtt"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    print(f"🗣️ Generating Audio + Subtitles...")

    # 2. Generate Audio AND Subtitles
    communicate = edge_tts.Communicate(full_script, "en-US-ChristopherNeural")
    submaker = edge_tts.SubMaker()
    
    with open(audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    # 3. Save the Subtitle file
    with open(subtitle_path, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())
        
    # Update JSON
    data['audio_path'] = audio_path
    data['subtitle_path'] = subtitle_path
    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Audio & Subs saved to: assets/{folder_name}/")

if __name__ == "__main__":
    asyncio.run(generate_voiceover("The_Glitch_in_the_Familiar.json"))
