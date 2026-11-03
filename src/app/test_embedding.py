import asyncio

from app.services.embedding_service import generate_embedding


async def main():
    print("Test started!")

    text = "FastAPI is a Python web framework."

    embedding = await generate_embedding(text)

    print("Embedding generated successfully!")
    print("Vector dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])


if __name__ == "__main__":
    asyncio.run(main())
