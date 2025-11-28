import requests
import json
import os
import random
import time
import shutil

def download_free_images(json_filename):
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find file {json_filename}")
        return

    folder_name = json_filename.replace(".json", "")
    os.makedirs(f"assets/{folder_name}", exist_ok=True)
    
    saved_paths = []
    
    print(f"🎨 Downloading {len(data['segments'])} images (Safe Mode)...")
    print("⏳ This will take about 2-3 minutes. Please be patient.")
    
    for i, segment in enumerate(data['segments']):
        prompt = segment['image_prompt']
        # Add random seed to avoid cached bad results
        seed = random.randint(1, 999999)
        enhanced_prompt = f"{prompt}, dark ambient, mystic, 8k resolution, cinematic lighting, hyperrealistic"
        
        image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width=720&height=1280&nologo=true"
        path = f"assets/{folder_name}/image_{i}.jpg"
        
        success = False
        
        # --- RETRY LOOP ---
        for attempt in range(3):
            try:
                print(f"   ⬇️  Downloading Image {i+1} (Attempt {attempt+1})...")
                
                # TIMEOUT INCREASED TO 90 SECONDS
                response = requests.get(image_url, timeout=90)
                
                if response.status_code == 200:
                    with open(path, 'wb') as file:
                        file.write(response.content)
                    saved_paths.append(path)
                    print(f"      ✅ Success!")
                    success = True
                    break
                else:
                    print(f"      ⚠️ Server Busy ({response.status_code}). Retrying...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"      ⚠️ Timeout/Error: {e}")
                time.sleep(3)
        
        # --- FALLBACK MECHANISM ---
        if not success:
            print(f"      ❌ Failed to generate Image {i+1}. Using fallback.")
            current_path = f"assets/{folder_name}/image_{i}.jpg"
            
            # Copy previous image if it exists
            if len(saved_paths) > 0:
                shutil.copy(saved_paths[-1], current_path)
                saved_paths.append(current_path)
                print("      ↪️ Duplicated previous image.")
            else:
                # If first image fails, create a black placeholder
                from PIL import Image
                img = Image.new('RGB', (720, 1280), color='black')
                img.save(current_path)
                saved_paths.append(current_path)
                print("      ⬛ Created black placeholder.")
        
        # Sleep between requests to be polite
        time.sleep(2)

    # Save results
    data['image_paths'] = saved_paths
    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"✅ Safe Download Complete.")

if __name__ == "__main__":
    # You can test it manually here
    download_free_images("The_Dead_Internet_Theory.json")
