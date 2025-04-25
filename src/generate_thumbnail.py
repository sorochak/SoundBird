from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import wikipedia

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Path to cached descriptions
CACHE_FILE = "bird_descriptions.json"

def load_cached_descriptions():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cached_descriptions(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_description_section(bird_species):
    try:
        page = wikipedia.page(bird_species, auto_suggest=False)
        content = page.content
        sections = content.split('\n==')

        for section in sections:
            if section.lower().startswith(" description") or "\n===Description" in section:
                return section.replace("===", "").replace("==", "").strip()
        
        return "[ERROR] No 'Description' section found in Wikipedia page."
    except Exception as e:
        return f"[ERROR] {e}"

def get_bird_description(bird_species):
    cache = load_cached_descriptions()
    if bird_species in cache:
        print(f"[INFO] Using cached description for '{bird_species}'")
        return cache[bird_species]

    try:
        description = get_description_section(bird_species)
        if "[ERROR]" not in description:
            print(f"[INFO] Detailed Wikipedia description found for '{bird_species}'")
            cache[bird_species] = description
            save_cached_descriptions(cache)
            return description
        else:
            print(f"[WARNING] Fallback to short summary for '{bird_species}'")
            summary = wikipedia.summary(bird_species, sentences=3, auto_suggest=False)
            cache[bird_species] = summary
            save_cached_descriptions(cache)
            return summary
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"[WARNING] Disambiguation for '{bird_species}', trying: {e.options[0]}")
        try:
            description = get_description_section(e.options[0])
            cache[bird_species] = description
            save_cached_descriptions(cache)
            return description
        except Exception as e2:
            print(f"[ERROR] Disambiguation fallback failed: {e2}")
    except wikipedia.exceptions.PageError:
        print(f"[WARNING] No Wikipedia page found for '{bird_species}'")
    except Exception as e:
        print(f"[ERROR] Wikipedia error: {e}")

    return f"A photorealistic image of a {bird_species} in its natural habitat, centered in the frame, soft natural background, good lighting."

def generate_image_prompt(bird_species, description):
    try:
        print("[INFO] Sending description to OpenAI to generate a concise prompt...")
        messages = [
            {"role": "system", "content": "You are a prompt writer for a photorealistic bird image generator."},
            {"role": "user", "content": f"Create a concise image generation prompt for a {bird_species}, based on this description:\n\n{description}\n\nKeep it under 4000 characters and include visual traits and environment."}
        ]
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate prompt: {e}")
        return f"A photorealistic image of a {bird_species} in its natural habitat. The bird is centered in frame with good lighting and visible feather details."

def generate_bird_thumbnail(bird_species):
    description = get_bird_description(bird_species)
    prompt = generate_image_prompt(bird_species, description)
    
    print(f"\n[DEBUG] Prompt:\n{prompt}\n")

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    return response.data[0].url


# Main test run
bird_species = "American Goldfinch"
description = get_bird_description(bird_species)
print("\n=== DESCRIPTION OUTPUT ===")
print(description)

image_url = generate_bird_thumbnail(bird_species)
print("\n=== IMAGE URL ===")
print(image_url)
