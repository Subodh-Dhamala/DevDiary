import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from google.genai import types

from app.services.rag_service import MAX_TOOL_ROUNDS, ask_question
from app.services.tool_executor import execute_tool


def function_call_response(name: str, arguments: dict) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            function_call=types.FunctionCall(
                                name=name,
                                args=arguments,
                            )
                        )
                    ],
                )
            )
        ]
    )


def text_response(text: str) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=text)],
                )
            )
        ]
    )


class ToolFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_answers_directly_without_calling_a_tool(self):
        session = object()
        with (
            patch(
                "app.services.rag_service.generate_tool_response",
                new_callable=AsyncMock,
                return_value=text_response("2 + 2 = 4."),
            ) as generate,
            patch(
                "app.services.rag_service.execute_tool",
                new_callable=AsyncMock,
            ) as execute,
        ):
            result = await ask_question("What is 2 + 2?", session)

        self.assertEqual(result, {"answer": "2 + 2 = 4.", "sources": []})
        generate.assert_awaited_once()
        execute.assert_not_awaited()

    async def test_read_only_request_only_offers_search(self):
        session = object()
        with patch(
            "app.services.rag_service.generate_tool_response",
            new_callable=AsyncMock,
            return_value=text_response("2 + 2 = 4."),
        ) as generate:
            await ask_question("What is 2 + 2?", session, allow_save=False)

        tools = generate.await_args.args[1]
        self.assertEqual(
            [declaration.name for declaration in tools[0].function_declarations],
            ["search_notes"],
        )

    async def test_read_only_request_rejects_save_calls(self):
        session = object()
        with (
            patch(
                "app.services.rag_service.generate_tool_response",
                new_callable=AsyncMock,
                return_value=function_call_response(
                    "save_note",
                    {"title": "Redis", "content": "Pub/Sub is ephemeral."},
                ),
            ),
            patch(
                "app.services.rag_service.execute_tool",
                new_callable=AsyncMock,
            ) as execute,
        ):
            with self.assertRaisesRegex(RuntimeError, "not available"):
                await ask_question("Remember this note.", session, allow_save=False)

        execute.assert_not_awaited()

    async def test_search_result_is_sent_back_and_returned_as_a_source(self):
        session = object()
        search_result = {
            "notes": [
                {"id": 7, "title": "Redis", "content": "Pub/Sub is ephemeral."}
            ]
        }
        with (
            patch(
                "app.services.rag_service.generate_tool_response",
                new_callable=AsyncMock,
                side_effect=[
                    function_call_response(
                        "search_notes",
                        {"query": "Redis Pub/Sub"},
                    ),
                    text_response("You noted that Redis Pub/Sub is ephemeral."),
                ],
            ) as generate,
            patch(
                "app.services.rag_service.execute_tool",
                new_callable=AsyncMock,
                return_value=search_result,
            ) as execute,
        ):
            result = await ask_question("What did I write about Redis?", session)

        self.assertEqual(
            result,
            {
                "answer": "You noted that Redis Pub/Sub is ephemeral.",
                "sources": [{"id": 7, "title": "Redis"}],
            },
        )
        execute.assert_awaited_once_with(
            "search_notes",
            {"query": "Redis Pub/Sub"},
            session,
        )
        self.assertEqual(generate.await_count, 2)
        follow_up = generate.await_args_list[1].args[0]
        self.assertIn("What did I write about Redis?", follow_up[0].parts[0].text)
        self.assertEqual(
            follow_up[2].parts[0].function_response.response,
            search_result,
        )

    async def test_tool_round_limit_stops_repeated_calls(self):
        session = object()
        with (
            patch(
                "app.services.rag_service.generate_tool_response",
                new_callable=AsyncMock,
                side_effect=[
                    function_call_response("search_notes", {"query": "Redis"})
                    for _ in range(MAX_TOOL_ROUNDS + 1)
                ],
            ),
            patch(
                "app.services.rag_service.execute_tool",
                new_callable=AsyncMock,
                return_value={"notes": []},
            ) as execute,
        ):
            with self.assertRaisesRegex(RuntimeError, "tool-call limit"):
                await ask_question("What did I save about Redis?", session)

        self.assertEqual(execute.await_count, MAX_TOOL_ROUNDS)

    async def test_save_note_validates_arguments_before_writing(self):
        session = object()
        with patch(
            "app.services.tool_executor.create_entry",
            new_callable=AsyncMock,
        ) as create:
            result = await execute_tool(
                "save_note",
                {
                    "title": "Redis",
                    "content": "Pub/Sub is ephemeral.",
                    "unexpected": True,
                },
                session,
            )

        self.assertEqual(result["error"], "Invalid tool arguments.")
        self.assertIn("unexpected", result["details"][0]["field"])
        create.assert_not_awaited()

    async def test_save_note_calls_entry_service_with_validated_data(self):
        session = object()
        saved_entry = SimpleNamespace(id=12, title="Redis")
        with patch(
            "app.services.tool_executor.create_entry",
            new_callable=AsyncMock,
            return_value=saved_entry,
        ) as create:
            result = await execute_tool(
                "save_note",
                {"title": " Redis ", "content": " Pub/Sub is ephemeral. "},
                session,
            )

        self.assertEqual(
            result,
            {"saved": True, "note": {"id": 12, "title": "Redis"}},
        )
        entry_data = create.await_args.args[0]
        self.assertEqual(entry_data.title, "Redis")
        self.assertEqual(entry_data.content, "Pub/Sub is ephemeral.")
        create.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
