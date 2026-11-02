
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

#create database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

#create a session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

#base class for database models
class Base(DeclarativeBase):
    pass


#dependency for database sessions
async def get_db():
    async with SessionLocal() as session:
        yield session
