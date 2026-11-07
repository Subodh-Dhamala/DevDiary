import logging
from contextlib import asynccontextmanager
from time import perf_counter
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine
from app.routes.entries import router as entries_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="DevDiary",
    lifespan=lifespan,
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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = perf_counter()
    response = await call_next(request)
    logger.info(
        "request method=%s path=%s status=%d duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started_at) * 1000,
    )
    return response


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, error: Exception):
    logger.error(
        "unhandled request error method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get(
    "/health",
    tags=["Health"],
    summary="Check API health",
    description="Returns a simple status indicating that the API is running.",
)
def health():
    return {"status": "ok"}
