
from typing import Any

#this is the orchestration layer that sends the question with both tools, executes only the function calls Gemini returns, sends their results back, and waits for Gemini’s final text.
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.generation_service import generate_tool_response
from app.services.tool_definitions import devdiary_tools, search_notes_declaration
from app.services.tool_executor import execute_tool

MAX_TOOL_ROUNDS = 3 #max retries


async def ask_question(
    question: str,
    session: AsyncSession,
    allow_save: bool = True,
) -> dict[str, Any]:
    tools = [devdiary_tools]
    if not allow_save:
        tools = [
            types.Tool(function_declarations=[search_notes_declaration])
        ]

    prompt = (
        "You are DevDiary, an assistant that can search and save the user's "
        "developer notes.\n"
        "For questions about what the user wrote or saved, use search_notes; "
        "answer those questions only from the returned notes. If no notes are "
        "found, say you could not find a relevant saved note.\n"
        "Only save notes when the user explicitly asks you to remember, save, "
        "or record information. If saving is unavailable, do not claim that "
        "you saved anything.\n"
        "For unrelated questions, answer directly without calling a tool.\n\n"
        f"User question: {question}"
    )
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])] # takes the prompt and wraps it in a Content object with the role of "user" and a Part object containing the text of the prompt
    #is the first call to gemini
    response = await generate_tool_response(contents, tools)
    sources: dict[int, dict[str, Any]] = {}
    tool_rounds = 0

    while response.function_calls:
        if tool_rounds >= MAX_TOOL_ROUNDS:
            raise RuntimeError(
                f"Model exceeded the {MAX_TOOL_ROUNDS}-round tool-call limit"
            )
        tool_rounds += 1

        if not response.candidates or response.candidates[0].content is None:
            raise RuntimeError("Model requested a tool without returning its call")

        function_responses = []
        for function_call in response.function_calls:
            if not function_call.name:
                raise RuntimeError("Model returned a function call without a name")
            if function_call.name == "save_note" and not allow_save:
                raise RuntimeError("save_note is not available for read-only requests")

            #the result will be used below to create a new content object that will be sent back to Gemini in the next call
            result = await execute_tool(
                function_call.name,
                function_call.args,
                session,
            )
            if function_call.name == "search_notes":
                for note in result.get("notes", []): #get the notes from the result
                    sources[note["id"]] = { #use the note id as the key and store the note id and title in the sources dictionary
                        "id": note["id"],
                        "title": note["title"],
                    }

            function_responses.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response=result,
                )
            )

        contents.extend(
            [
                response.candidates[0].content,
                types.Content(role="user", parts=function_responses),
            ]
        )
        response = await generate_tool_response(contents, tools)

    if not response.text:
        raise RuntimeError("Model returned neither a final answer nor a tool call")

    return {
        "answer": response.text,
        "sources": list(sources.values()),
    }
