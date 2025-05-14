# image_generator.py
from config import client
from wiki_utils import get_bird_description


def generate_image_prompt(bird_species, description):
    """
    Sends a bird description to OpenAI's chat model to generate a concise image prompt.
    Args:
        bird_species (str): Name of the bird.
        description (str): Wikipedia-derived description of the bird.
    Returns:
        str: A short, image-generation-friendly prompt.
    """

    try:
        print("[INFO] Sending description to OpenAI to generate a concise prompt...")
        messages = [
            {
                "role": "system",
                "content": "You are a prompt writer for photorealistic bird images. Do not include measurements, text labels, diagrams, or species comparisons. Focus on feather color, posture, and environment only.",
            },
            {
                "role": "user",
                "content": f"Create a concise image generation prompt for a {bird_species}, based on this description:\n\n{description}\n\nKeep it under 4000 characters and include visual traits and environment.",
            },
        ]
        chat_response = client.chat.completions.create(
            model="gpt-4", messages=messages, temperature=0.7
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate prompt: {e}")
        return f"A photorealistic image of a {bird_species} in its natural habitat. The bird is centered in frame with good lighting and visible feather details."


def generate_bird_thumbnail(bird_species):
    """
    Generates a DALL·E 3 image of a bird species using Wikipedia and OpenAI to build a detailed prompt.
    Args:
        bird_species (str): Name of the bird to generate.
    Returns:
        str: URL of the generated image.
    """
    description = get_bird_description(bird_species)
    prompt = generate_image_prompt(bird_species, description)

    print(f"\n[DEBUG] Prompt:\n{prompt}\n")

    response = client.images.generate(
        model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
    )

    return response.data[0].url
