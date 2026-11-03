from fastapi import FastAPI
from app.routes.entries import router as entries_router

app = FastAPI(title = "DevDiary")
app.include_router(entries_router, prefix="/api/v1") #connects all endpoints registered on that router here.

@app.get("/health")
def health():
    return {"status": "ok"}
