# wiki_utils.py
# This module contains utility functions for working with Wikipedia data.
import os
import json
import wikipedia

# Path to cached descriptions
CACHE_FILE = "bird_descriptions.json"

def load_cached_descriptions():
    """
    Load cached bird descriptions from a local JSON file.
    Returns:
        dict: Cached descriptions keyed by bird species.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cached_descriptions(cache):
    """
    Save bird descriptions to the local JSON cache.
    Args:
        cache (dict): Dictionary of bird species to descriptions.
    """
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_description_section(bird_species):
    """
    Attempts to extract the 'Description' section from a Wikipedia article.
    Args:
        bird_species (str): Name of the bird species.
    Returns:
        str: The extracted description or an error message.
    """
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
    """
    Retrieves a bird's description from the cache or Wikipedia.
    Args:
        bird_species (str): Name of the bird species.
    Returns:
        str: A textual description of the bird.
    """
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