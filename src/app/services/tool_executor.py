#this file contains the logic for executing the tools defined in tool_definitions.py. It validates the input arguments, calls the appropriate service functions, and returns the results or errors.

from typing import Annotated, Any # typing module provides support for type hints and annotations, annotated means that the type can have additional metadata associated with it and any means that the type can be any type, without any specific constraints or restrictions.
from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import EntryCreate
from app.services.entry_service import create_entry, search_entries


class SearchNotesArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")  #rejects extra fields

    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SaveNoteArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]
    content: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=50_000),
    ]


#this function executes the tool recommended via tool_definitions.py
#name is name of tool , arguments is input parameters, session is db session
async def execute_tool(
    name: str,
    arguments: Any,
    session: AsyncSession,
) -> dict[str, Any]:
    if name not in {"search_notes", "save_note"}:
        raise ValueError(f"Unknown tool requested by model: {name}")

    try:
        if name == "search_notes":
            validated = SearchNotesArguments.model_validate(arguments)
            entries = await search_entries(validated.query, session)
            return {
                "notes": [
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "content": entry.content,
                    }
                    for entry in entries
                ]
            }

        validated = SaveNoteArguments.model_validate(arguments)
        entry = await create_entry(
            EntryCreate(title=validated.title, content=validated.content),
            session,
        )
        return {
            "saved": True,
            "note": {
                "id": entry.id,
                "title": entry.title,
            },
        }
    except ValidationError as error:
        return {
            "error": "Invalid tool arguments.",
            "details": [
                {
                    "field": ".".join(str(part) for part in issue["loc"]),
                    "message": issue["msg"],
                }
                for issue in error.errors()
            ],
        }
