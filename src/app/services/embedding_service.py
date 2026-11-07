from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())


async def generate_embedding(text: str) -> list[float]:
    response = await client.aio.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={"output_dimensionality": 1536},
    )

    return response.embeddings[0].values
