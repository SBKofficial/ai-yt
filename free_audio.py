import json
import edge_tts
import asyncio
import os

async def generate_voiceover(json_filename):
    # 1. Load the data
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    # 2. Extract the text
    # We combine all segments into one long string for a smooth flow
    full_script = " ".join([seg['text'] for seg in data['segments']])
    
    print(f"🗣️  Generating Voiceover ({len(full_script.split())} words)...")
    
    output_path = f"assets/{json_filename.replace('.json', '')}/voiceover.mp3"
    
    # Ensure folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 3. Generate Audio
    # "en-US-ChristopherNeural" is a deep, movie-trailer style voice
    communicate = edge_tts.Communicate(full_script, "en-US-ChristopherNeural")
    
    await communicate.save(output_path)
    
    # Save audio path to JSON
    data['audio_path'] = output_path
    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Audio saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(generate_voiceover("The_Dead_Internet_Theory.json"))
