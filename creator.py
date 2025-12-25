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
    Tries models in order of quality: 2.5 -> 1.5 -> Pro
    """
    models_to_try = [
        'gemini-2.5-flash',      
        'gemini-1.5-flash',      
        'gemini-1.5-pro-latest', 
        'gemini-pro'             
    ]

    for model_name in models_to_try:
        try:
            print(f"   🤖 Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"   ⚠️ {model_name} failed. Trying next...")
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
    # --- THE RETENTION UPGRADE (FIXED) ---
    prompt = f"""
    You are an elite viral screenwriter for YouTube Shorts. Write a script about: {topic}.
    
    CRITICAL RULES:
    1. TOTAL DURATION: Strictly 45 seconds.
    2. SEGMENTATION: You MUST break the script into exactly 8 distinct segments.
    3. WORD COUNT: Maximum 15 words per segment. (Total ~110 words).
    4. VISUAL PACING: Every image prompt must specify a DIFFERENT camera angle (Close-up, Wide Shot, Low Angle, Drone View).
    
    Structure as valid JSON only:
    {{
        "title": "Clickbait Title (ALL CAPS, under 50 chars)",
        "viral_comment": "A controversial question related to the topic to pin",
        "segments": [
            {{
                "text": "Hook: {topic} is not what you think.",
                "image_prompt": "Hyper-realistic extreme close-up of {topic}, dark atmosphere, 8k"
            }},
            {{
                "text": "Most people believe [Common Myth]...",
                "image_prompt": "Cinematic wide shot of people looking confused, dark noir style"
            }},
            {{
                "text": "...but the truth is terrifying.",
                "image_prompt": "Glitch art style, distorted reality, scary atmosphere"
            }}
            // ... Continue for exactly 8 segments total
        ]
    }}
    """

    print(f"🧠 Brainstorming High-Retention Script: {topic}...")

    try:
        response_text = generate_with_fallback(prompt)

        # Clean JSON (Gemini sometimes adds markdown blocks)
        clean_text = response_text.replace('```json', '').replace('```', '')
        clean_text = clean_text.strip() 
        
        data = json.loads(clean_text)

        safe_name = sanitize_filename(topic)
        filename = f"{safe_name}.json"

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        return filename

    except Exception as e:
        print(f"❌ Script Error: {e}")
        if 'response_text' in locals():
             print(f"Failed JSON text was: {response_text[:100]}...")
        return None
