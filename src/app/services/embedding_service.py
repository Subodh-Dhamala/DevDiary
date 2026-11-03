import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=api_key)

async def generate_embedding(text:str) -> list[float]:
 response = await client.aio.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 1536
        }
    )

    return response.embeddings[0].values