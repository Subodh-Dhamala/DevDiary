from fastapi import FastAPI
from app.routes.entries import router as entries_router

app = FastAPI(
    title="DevDiary",
    description=(
        "API for storing developer notes, searching them semantically, and "
        "asking an assistant questions about them.\n\n"
        "Use `GET /api/v1/entries/ask` for a read-only assistant request. "
        "`POST /api/v1/entries/ask` also allows the assistant to save a note "
        "when explicitly asked. Use `GET /api/v1/entries/search` to retrieve "
        "matching entries directly."
    ),
    openapi_tags=[
        {
            "name": "Assistant",
            "description": "Ask questions about saved notes or request a note be saved.",
        },
        {
            "name": "Entries",
            "description": "Create, retrieve, search, update, and delete notes.",
        },
        {
            "name": "Health",
            "description": "Check whether the API is running.",
        },
    ],
)
app.include_router(entries_router, prefix="/api/v1") #connects all endpoints registered on that router here.

@app.get(
    "/health",
    tags=["Health"],
    summary="Check API health",
    description="Returns a simple status indicating that the API is running.",
)
def health():
    return {"status": "ok"}
