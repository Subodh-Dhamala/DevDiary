import asyncio

from app.database import engine


async def test_connection():
    async with engine.connect() as connection:
        result = await connection.exec_driver_sql("SELECT version()")
        print("Connected successfully!")
        print(result.scalar())

    await engine.dispose()


asyncio.run(test_connection())
