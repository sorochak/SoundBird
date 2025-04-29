# wiki_utils.py
# This module contains utility functions for working with Wikipedia data.
import os
import json
import wikipedia
import logging

# Set up simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        sections = content.split("\n==")

        for section in sections:
            if (
                section.lower().startswith(" description")
                or "\n===Description" in section
            ):
                return section.replace("===", "").replace("==", "").strip()

        return "[ERROR] No 'Description' section found in Wikipedia page."
    except Exception as e:
        return f"[ERROR] {e}"


def get_bird_description(bird_species):
    """
    Retrieves a bird's description from the cache or Wikipedia.
    Falls back to a safe generic prompt if no detailed description is found.
    """
    cache = load_cached_descriptions()
    if bird_species in cache:
        logger.info(f"[CACHE] Using cached description for '{bird_species}'")
        return cache[bird_species]

    try:
        description = get_description_section(bird_species)
        if "[ERROR]" not in description:
            logger.info(
                f"[WIKI] Detailed Wikipedia description found for '{bird_species}'"
            )
            cache[bird_species] = description
            save_cached_descriptions(cache)
            return description
        else:
            logger.warning(
                f"[FALLBACK] No 'Description' section found for '{bird_species}'. Using safe fallback prompt."
            )
    except wikipedia.exceptions.DisambiguationError as e:
        logger.warning(
            f"[DISAMBIGUATION] Multiple pages for '{bird_species}': {e.options}. Fallback triggered."
        )
    except wikipedia.exceptions.PageError:
        logger.warning(
            f"[MISSING PAGE] No Wikipedia page found for '{bird_species}'. Fallback triggered."
        )
    except Exception as e:
        logger.error(f"[ERROR] Unexpected Wikipedia error for '{bird_species}': {e}")

    # Fallback: safe default prompt
    fallback_description = f"A photorealistic image of a {bird_species} in its natural habitat. The bird is centered in frame with good lighting and visible feather details."
    cache[bird_species] = fallback_description
    save_cached_descriptions(cache)
    return fallback_description
