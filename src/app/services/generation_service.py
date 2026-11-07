from google.genai import types

from app.services.embedding_service import client


async def generate_answer(prompt: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    return response.text



async def generate_tool_response(
    contents: str | list[types.Content], #the parameter can be single or multiple content
    tools: list[types.Tool], # has our devdiary_tools
) -> types.GenerateContentResponse:
    config = types.GenerateContentConfig(
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True # we control the tool calling logic in rag_service.py, so we disable automatic function calling here
        ),
    )

    return await client.aio.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=config,
    )