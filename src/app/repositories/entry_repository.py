from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entry import Entry

SEARCH_DISTANCE_THRESHOLD = 0.3
SEARCH_RESULT_LIMIT = 5


async def create_entry(entry: Entry, session: AsyncSession) -> Entry:
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_all_entries(session: AsyncSession) -> list[Entry]:
    result = await session.execute(select(Entry))
    return list(result.scalars().all())


async def get_entry_by_id(
    entry_id: int,
    session: AsyncSession,
) -> Entry | None:
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    return result.scalar_one_or_none()


async def save_entry(entry: Entry, session: AsyncSession) -> Entry:
    await session.commit()
    await session.refresh(entry)
    return entry


async def delete_entry(entry: Entry, session: AsyncSession) -> Entry:
    await session.delete(entry)
    await session.commit()
    return entry


async def search_entries(
    query_embedding: list[float],
    session: AsyncSession,
) -> list[Entry]:
    distance = Entry.embedding.cosine_distance(query_embedding)
    statement = (
        select(Entry)
        .where(distance < SEARCH_DISTANCE_THRESHOLD)
        .order_by(distance)
        .limit(SEARCH_RESULT_LIMIT)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())
