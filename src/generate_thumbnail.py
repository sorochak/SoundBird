from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

def generate_bird_thumbnail(bird_species):
  prompt = f"Create a detailed and lifelike image of a {bird_species} in its natural habitat, focusing on the bird to capture its unique characteristics and colors accurately. The bird should be centered in the frame, making it ideal for use as a thumbnail image. The background should be simple and not distract from the bird, subtly hinting at the bird's natural environment without overpowering the subject. Ensure the lighting is clear, highlighting the bird's features, making it easily recognizable at a glance."

  response = client.images.generate(
    model="dall-e-2",
    prompt=prompt,
    n=1,
    size="512x512",
    # quality="standard",
    # style="natural"
  )

  # This will return the URL to the generated image
  return response.data[0].url

# Example usage
bird_species = "American Robin"
image_url = generate_bird_thumbnail(bird_species)
print(image_url) 