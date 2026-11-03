
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entry import Entry
from app.schemas import EntryCreate, EntryUpdate


async def create_entry(
    entry_data: EntryCreate,
    session: AsyncSession,
):
    new_entry = Entry(
        title=entry_data.title,
        content=entry_data.content,
    )

    session.add(new_entry)

    await session.commit()
    await session.refresh(new_entry)

    return new_entry


async def get_all_entries(session: AsyncSession):
    result = await session.execute(select(Entry))

    return result.scalars().all()


async def get_entry_by_id(
    entry_id: int,
    session: AsyncSession,
):
    result = await session.execute(
        select(Entry).where(Entry.id == entry_id)
    )

    return result.scalar_one_or_none()


async def update_entry(
    entry_id: int,
    entry_data: EntryUpdate,
    session: AsyncSession,
):
    entry = await get_entry_by_id(entry_id, session)

    if entry is None:
        return None

    if entry_data.title is not None:
        entry.title = entry_data.title

    if entry_data.content is not None:
        entry.content = entry_data.content

    await session.commit()
    await session.refresh(entry)

    return entry


async def delete_entry(entry_id: int, session: AsyncSession):
    entry = await get_entry_by_id(entry_id, session)

    if entry is None:
        return None

    await session.delete(entry)
    await session.commit()

    return entry
