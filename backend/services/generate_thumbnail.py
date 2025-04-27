# generate_thumbnail.py
import argparse
from wiki_utils import get_bird_description
from image_generator import generate_bird_thumbnail

def main():
    parser = argparse.ArgumentParser(description="Generate a bird thumbnail using Wikipedia and OpenAI")
    parser.add_argument("bird_species", type=str, help="Name of the bird species (e.g. 'American Goldfinch')")
    args = parser.parse_args()

    bird_species = args.bird_species
    image_url = generate_bird_thumbnail(bird_species)

    print("\n=== IMAGE URL ===")
    print(image_url)

if __name__ == "__main__":
    main()
