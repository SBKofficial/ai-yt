import google.generativeai as genai
import json
import os

# 1. Setup (Keep your key here)
genai.configure(api_key="AIzaSyAd_FrvRr8SMeWbrcJiJ4cGbvTNqSdE4mI")

def generate_free_script(topic):
    # CHANGED: Updated model name to 'gemini-2.5-flash' (Current Standard)
    # If this fails, try 'gemini-1.5-flash'
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a dark mystery storyteller. Write a 50-second YouTube Shorts script about: {topic}.
    
    Structure the response as valid JSON only:
    {{
        "title": "Short catchy title",
        "segments": [
            {{
                "text": "The first sentence...",
                "image_prompt": "Dark cinematic 8k wallpaper of {topic}, mysterious atmosphere"
            }},
            {{
                "text": "The second sentence...",
                "image_prompt": "Abstract horror art of..."
            }}
        ]
    }}
    """
    
    print(f"🧠 Asking Gemini about: {topic}...")
    
    try:
        response = model.generate_content(prompt)
        
        # Clean the response (Gemini sometimes adds markdown blocks)
        clean_text = response.text.replace('```json', '').replace('```', '')
        data = json.loads(clean_text)
        
        # Save it
        filename = f"{topic.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Script saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Hint: Run the 'check_models.py' script below to see which models you have access to.")
# Add this to the bottom of free_creator.py

def get_viral_topic(history_file="history.txt"):
    # 1. Load history so we don't repeat topics
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            existing_topics = f.read()
    else:
        existing_topics = ""

    # 2. Ask Gemini for a NEW topic
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a YouTube Strategist. Generate ONE viral, dark mystery, or paradox topic.
    
    Rules:
    1. It must be scary, mysterious, or mind-blowing.
    2. It must NOT be in this list: {existing_topics}
    3. Return ONLY the topic name (no quotes, no explanation).
    
    Example output: The Rake
    """
    
    try:
        response = model.generate_content(prompt)
        topic = response.text.strip()
        
        # 3. Save to history immediately
        with open(history_file, "a") as f:
            f.write(topic + "\n")
            
        print(f"🤖 AI Auto-Selected Topic: {topic}")
        return topic
        
    except Exception as e:
        print(f"❌ Error generating topic: {e}")
        return "The Backrooms" # Fallback topic if AI fails
    
if __name__ == "__main__":
    generate_free_script("The Dead Internet Theory")
