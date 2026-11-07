
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import AskRequest, EntryCreate, EntryUpdate, EntryResponse
from app.services import entry_service

from app.services.rag_service import ask_question


router = APIRouter()

@router.get(
    "/entries/ask",
    tags=["Assistant"],
    summary="Ask about saved notes (read-only)",
    description=(
        "Ask a question using the saved-note assistant. The assistant may "
        "search notes but cannot save notes through this endpoint."
    ),
)
async def ask(
    question: str,
    db: AsyncSession = Depends(get_db),
):

    result = await ask_question(question, db, allow_save=False)

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    }


@router.post(
    "/entries/ask",
    tags=["Assistant"],
    summary="Ask the assistant",
    description=(
        "Ask a question using the saved-note assistant. The assistant can "
        "search notes and may save a note when explicitly asked."
    ),
)
async def ask_with_tools(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await ask_question(request.question, db)

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
    }


@router.get(
    "/entries/search",
    response_model=list[EntryResponse],
    tags=["Entries"],
    summary="Search entries by meaning",
    description=(
        "Returns up to five entries whose embedding is within the configured "
        "cosine-distance threshold of the query."
    ),
)
async def search_entries(
    query: str,
    db: AsyncSession = Depends(get_db),
):
    return await entry_service.search_entries(query, db)

@router.post(
    "/entries",
    status_code=201,
    response_model=EntryResponse,
    tags=["Entries"],
    summary="Create an entry",
    description="Creates a note and generates its embedding for semantic search.",
)
async def create_entry(
    entry: EntryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await entry_service.create_entry(entry, db)


@router.get(
    "/entries",
    response_model=list[EntryResponse],
    tags=["Entries"],
    summary="List entries",
    description="Returns all saved entries.",
)
async def get_entries(db: AsyncSession = Depends(get_db)):
    return await entry_service.get_all_entries(db)


@router.get(
    "/entries/{entry_id}",
    response_model=EntryResponse,
    tags=["Entries"],
    summary="Get an entry",
    description="Returns one entry by its ID.",
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
    response_model=EntryResponse,
    tags=["Entries"],
    summary="Update an entry",
    description="Updates an entry and regenerates its embedding.",
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


@router.delete(
    "/entries/{entry_id}",
    status_code=204,
    tags=["Entries"],
    summary="Delete an entry",
    description="Deletes an entry by its ID. Returns no content on success.",
)
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
