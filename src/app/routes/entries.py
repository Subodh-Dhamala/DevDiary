from fastapi import APIRouter, HTTPException, Response
from app.schemas import EntryCreate, EntryUpdate
from app.services import entry_service

router = APIRouter()


@router.post("/entries", status_code=201)
def create_entry(entry: EntryCreate):
    return entry_service.create_entry(entry)


@router.get("/entries")
def get_entries():
    return entry_service.get_all_entries()


@router.get("/entries/{entry_id}")
def get_entry(entry_id: int):
    entry = entry_service.get_entry_by_id(entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry


@router.patch("/entries/{entry_id}")
def update_entry(entry_id: int, entry_update: EntryUpdate):
    entry = entry_service.update_entry(entry_id, entry_update)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )

    return entry


@router.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int):
    deleted_entry = entry_service.delete_entry(entry_id)

    if deleted_entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entry with id {entry_id} not found"
        )


    return Response(status_code=204)