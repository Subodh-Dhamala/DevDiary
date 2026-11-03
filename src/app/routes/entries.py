
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import EntryCreate, EntryUpdate, EntryResponse
from app.services import entry_service


router = APIRouter()

@router.get("/entries/search", response_model=list[EntryResponse])
async def search_entries(
    query: str,
    db: AsyncSession = Depends(get_db),
):
    return await entry_service.search_entries(query, db)

@router.post(
    "/entries",
    status_code=201,
    response_model=EntryResponse
)
async def create_entry(
    entry: EntryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await entry_service.create_entry(entry, db)


@router.get(
    "/entries",
    response_model=list[EntryResponse]
)
async def get_entries(db: AsyncSession = Depends(get_db)):
    return await entry_service.get_all_entries(db)


@router.get(
    "/entries/{entry_id}",
    response_model=EntryResponse
)
async def get_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    entry = await entry_service.get_entry_by_id(entry_id, db)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry


@router.patch(
    "/entries/{entry_id}",
    response_model=EntryResponse
)
async def update_entry(
    entry_id: int,
    entry_update: EntryUpdate,
    db: AsyncSession = Depends(get_db)
):
    entry = await entry_service.update_entry(entry_id, entry_update, db)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry


@router.delete("/entries/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted_entry = await entry_service.delete_entry(entry_id, db)

    if deleted_entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

    return Response(status_code=204)

