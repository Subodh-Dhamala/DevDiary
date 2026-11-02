from pydantic import BaseModel

class EntryCreate(BaseModel):
    title: str
    content:str

class EntryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None