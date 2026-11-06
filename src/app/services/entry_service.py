
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entry import Entry
from app.schemas import EntryCreate, EntryUpdate

from app.services.embedding_service import generate_embedding

async def create_entry(entry_data: EntryCreate, session: AsyncSession):
    text = f"{entry_data.title}\n\n{entry_data.content}"

    embedding = await generate_embedding(text) #embedding generation for the entry

    new_entry = Entry(
        title=entry_data.title,
        content=entry_data.content,
        embedding=embedding,
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

    text = f"{entry.title}\n\n{entry.content}"
    entry.embedding = await generate_embedding(text) #update embedding for the entry

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


async def search_entries(query: str, session: AsyncSession):
    #generate embedding for the search query
    query_embedding = await generate_embedding(query)

    distance = Entry.embedding.cosine_distance(query_embedding)  # calculates the cosine distance between the query embedding and the entry embeddings

    #selects entries with a cosine distance less than 0.3, orders them by distance and limits the results to the top 5 entries
    statement = (
        select(Entry)
        .where(distance < 0.3) #decision threshold for similarity
        .order_by(distance)
        .limit(5)
    )

    result = await session.execute(statement)

    return result.scalars().all()