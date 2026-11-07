import asyncio

from app.services.embedding_service import client


async def main():
    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Explain Redis caching in simple terms."
    )

    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())