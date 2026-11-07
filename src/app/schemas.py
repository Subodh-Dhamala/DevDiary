
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator


EntryTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]
EntryContent = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50_000),
]
AskQuestion = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4_000),
]
SearchQuery = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1_000),
]


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EntryCreate(RequestModel):
    title: EntryTitle
    content: EntryContent


class EntryUpdate(RequestModel):
    title: EntryTitle | None = None
    content: EntryContent | None = None

    @model_validator(mode="after")
    def require_update_fields(self):
        if self.title is None and self.content is None:
            raise ValueError("At least one of title or content must be provided")
        return self


class AskRequest(RequestModel):
    question: AskQuestion


class EntryResponse(BaseModel):
    id: int
    title: str
    content: str
    embedding: list[float] | None = None
    created_at: datetime
    updated_at: datetime

    #pydantic reads the attributes from the SQLAlchemy model and converts them to the Pydantic model
    model_config = ConfigDict(from_attributes=True)
