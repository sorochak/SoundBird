import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from project root (two levels up from this file)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
