import google.generativeai as genai
import json
import os
import re
import time

# Setup API Key
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def sanitize_filename(name):
    clean_name = re.sub(r'[^\w\s-]', '', name)
    return clean_name.strip().replace(' ', '_')

def generate_with_fallback(prompt):
    """
    Tries multiple model versions until one works.
    """
    # PRIORITY LIST FOR LATE 2025:
    models_to_try = [
        'gemini-2.5-flash', # Your requested model
        'gemini-1.5-flash', # Backup fast model
        'gemini-1.5-pro',   # Backup smart model
        'gemini-2.0-flash'  # Alternative
    ]
    
    for model_name in models_to_try:
        try:
            print(f"   🤖 Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"   ⚠️ {model_name} failed ({str(e)[:50]}...). Trying next...")
            time.sleep(1)
            
    raise Exception("❌ ALL models failed. Check your API Key permissions.")

def get_viral_topic(history_file="history.txt"):
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            existing_topics = f.read()
    else:
        existing_topics = ""

    prompt = f"""
    You are a YouTube Strategist for 'Echoes of Reality'.
    Generate ONE viral, dark mystery, paradox, or cosmic horror topic.
    Rules:
    1. It must be scary, mysterious, or mind-blowing.
    2. It must NOT be in this list: {existing_topics}
    3. Return ONLY the topic name (no quotes).
    """
    
    try:
        topic_text = generate_with_fallback(prompt)
        topic = topic_text.strip()
        
        # Save to history
        with open(history_file, "a") as f:
            f.write(topic + "\n")
            
        print(f"🤖 Topic Selected: {topic}")
        return topic
        
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return "The Dark Forest Theory" 

def generate_free_script(topic):
    prompt = f"""
    You are a dark mystery storyteller. Write a 50-second YouTube Shorts script about: {topic}.
    Structure the response as valid JSON only:
    {{
        "title": "Short catchy title",
        "segments": [
            {{
                "text": "Hook sentence...",
                "image_prompt": "Dark cinematic 8k wallpaper of {topic}"
            }},
            {{
                "text": "Body sentence...",
                "image_prompt": "Abstract horror art of..."
            }}
        ]
    }}
    """
    
    print(f"🧠 Brainstorming: {topic}...")
    
    try:
        response_text = generate_with_fallback(prompt)
        
        # Clean JSON
        clean_text = response_text.replace('```json', '').replace('```', '')
        data = json.loads(clean_text)
        
        safe_name = sanitize_filename(topic)
        filename = f"{safe_name}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
            
        return filename
        
    except Exception as e:
        print(f"❌ Script Error: {e}")
        return None
