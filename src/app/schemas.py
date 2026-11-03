
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    title: str
    content: str


class EntryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class EntryResponse(BaseModel):
    id: int
    title: str
    content: str
    embedding: list[float] | None = None
    created_at: datetime
    updated_at: datetime

    #pydantic reads the attributes from the SQLAlchemy model and converts them to the Pydantic model
    model_config = ConfigDict(from_attributes=True)
