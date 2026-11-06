import asyncio

from google.genai import types

from app.services.embedding_service import client
from app.services.tool_definitions import devdiary_tools


async def test_function_calling():

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Who is batman?",
        config=types.GenerateContentConfig(
            # give the tools to the model so it can call them
            tools=[devdiary_tools],

    #this configures the model to call the search_notes function when it thinks it's appropriate, based on the question asked
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY", #forces gemini to request a function call 
                    allowed_function_names=["search_notes"], #restrict the model to only call the search_notes function, even though both tools are provided
                )
            ),

            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

    print("Full response:")
    print(response)

    print("\nFunction calls:")
    print(response.function_calls)

    print("\nText:")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(test_function_calling())