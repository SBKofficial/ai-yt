import google.generativeai as genai
import json
import os
import re

# 1. Setup API Key
# This looks for the key in your Environment (GitHub Secrets)
# If you run this locally on your PC, make sure to set the environment variable
# or temporarily paste your key string below for testing.
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables.")
    # You can paste your key here for local testing if needed:
    # api_key = "YOUR_PASTED_KEY_HERE"

genai.configure(api_key=api_key)

def sanitize_filename(name):
    """
    Removes illegal characters from filenames (like : ? * " < > |).
    Converts 'The Anomaly: What happened?' -> 'The_Anomaly_What_happened'
    """
    # Remove anything that isn't a letter, number, space, or hyphen
    clean_name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores and strip whitespace
    return clean_name.strip().replace(' ', '_')

def get_viral_topic(history_file="history.txt"):
    """
    Asks AI for a unique viral topic that hasn't been done before.
    """
    # Load history so we don't repeat topics
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            existing_topics = f.read()
    else:
        existing_topics = ""

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a YouTube Strategist for a channel called 'Echoes of Reality'.
    Generate ONE viral, dark mystery, paradox, or cosmic horror topic.
    
    Rules:
    1. It must be scary, mysterious, or mind-blowing.
    2. It must NOT be in this list: {existing_topics}
    3. Return ONLY the topic name (no quotes, no explanation).
    4. Do not use colons (:) in the topic name if possible.
    
    Example output: The Rake
    """
    
    try:
        response = model.generate_content(prompt)
        topic = response.text.strip()
        
        # Save to history immediately
        with open(history_file, "a") as f:
            f.write(topic + "\n")
            
        print(f"🤖 AI Auto-Selected Topic: {topic}")
        return topic
        
    except Exception as e:
        print(f"❌ Error generating topic: {e}")
        # Fallback topic if AI fails
        return "The Dark Forest Theory" 

def generate_free_script(topic):
    """
    Generates the Video Script and Image Prompts, then saves as JSON.
    """
    # Use the fast, free model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a dark mystery storyteller. Write a 50-second YouTube Shorts script about: {topic}.
    
    Structure the response as valid JSON only:
    {{
        "title": "Short catchy title for YouTube",
        "segments": [
            {{
                "text": "The first sentence (Hook)...",
                "image_prompt": "Dark cinematic 8k wallpaper of {topic}, mysterious atmosphere, hyperrealistic"
            }},
            {{
                "text": "The second sentence...",
                "image_prompt": "Abstract horror art of..."
            }}
        ]
    }}
    """
    
    print(f"🧠 Brainstorming script for: {topic}...")
    
    try:
        response = model.generate_content(prompt)
        
        # Clean the response (Gemini sometimes adds ```json markers)
        clean_text = response.text.replace('```json', '').replace('```', '')
        data = json.loads(clean_text)
        
        # --- SANITIZE FILENAME (CRITICAL FIX) ---
        safe_name = sanitize_filename(topic)
        filename = f"{safe_name}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Script saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return None

if __name__ == "__main__":
    # Test run
    test_topic = get_viral_topic()
    generate_free_script(test_topic)
