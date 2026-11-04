from app.services.embedding_service import client


async def generate_answer(prompt: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text