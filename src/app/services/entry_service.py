
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entry import Entry
from app.repositories import entry_repository
from app.schemas import EntryCreate, EntryUpdate
from app.services.embedding_service import generate_embedding


async def create_entry(entry_data: EntryCreate, session: AsyncSession) -> Entry:
    text = f"{entry_data.title}\n\n{entry_data.content}"
    entry = Entry(
        title=entry_data.title,
        content=entry_data.content,
        embedding=await generate_embedding(text),
    )
    return await entry_repository.create_entry(entry, session)


async def get_all_entries(session: AsyncSession) -> list[Entry]:
    return await entry_repository.get_all_entries(session)


async def get_entry_by_id(
    entry_id: int,
    session: AsyncSession,
) -> Entry | None:
    return await entry_repository.get_entry_by_id(entry_id, session)


async def update_entry(
    entry_id: int,
    entry_data: EntryUpdate,
    session: AsyncSession,
) -> Entry | None:
    entry = await entry_repository.get_entry_by_id(entry_id, session)

    if entry is None:
        return None

    if entry_data.title is not None:
        entry.title = entry_data.title

    if entry_data.content is not None:
        entry.content = entry_data.content

    text = f"{entry.title}\n\n{entry.content}"
    entry.embedding = await generate_embedding(text) #update embedding for the entry

    return await entry_repository.save_entry(entry, session)


async def delete_entry(entry_id: int, session: AsyncSession) -> Entry | None:
    entry = await entry_repository.get_entry_by_id(entry_id, session)

    if entry is None:
        return None

    return await entry_repository.delete_entry(entry, session)


async def search_entries(query: str, session: AsyncSession) -> list[Entry]:
    query_embedding = await generate_embedding(query)

    return await entry_repository.search_entries(query_embedding, session)