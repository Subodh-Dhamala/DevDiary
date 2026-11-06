#this file tells gemini what tools it can use, and tool_executor.py executes the tools.
from google.genai import types

search_notes_declaration = types.FunctionDeclaration(
    name="search_notes",
    description=(
        "Search the user's saved developer notes when they ask what they "
        "previously wrote, learned, or saved about a topic. Search by "
        "meaning, not just exact wording."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": { #defines the expected input parameters 
            "query": {  # the argument name
                "description": "A concise topic or question to find in saved notes.",
            }
        },
        "required": ["query"],
    },
)

save_note_declaration = types.FunctionDeclaration(
    name="save_note",
    description=(
        "Save information as a new developer note when the user explicitly "
        "asks you to remember, save, or record it. Do not use this to answer "
        "a question or to save information without the user's request."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the note.",
            },
            "content": {
                "type": "string",
                "description": "The content of the note.",
            },
        },
        "required": ["title", "content"],
    },
)

devdiary_tools = types.Tool(
    function_declarations=[
        search_notes_declaration,
        save_note_declaration,
    ]
)
