import unittest
from unittest.mock import AsyncMock, patch

from app.models.entry import Entry
from app.schemas import EntryCreate
from app.services.entry_service import create_entry, search_entries


class EntryServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_generates_embedding_then_saves_through_repository(self):
        session = object()
        persisted_entry = Entry(
            id=3,
            title="Redis",
            content="Pub/Sub is ephemeral.",
            embedding=[0.1],
        )
        with (
            patch(
                "app.services.entry_service.generate_embedding",
                new_callable=AsyncMock,
                return_value=[0.1],
            ) as embed,
            patch(
                "app.services.entry_service.entry_repository.create_entry",
                new_callable=AsyncMock,
                return_value=persisted_entry,
            ) as save,
        ):
            result = await create_entry(
                EntryCreate(title="Redis", content="Pub/Sub is ephemeral."),
                session,
            )

        self.assertIs(result, persisted_entry)
        embed.assert_awaited_once_with("Redis\n\nPub/Sub is ephemeral.")
        stored_entry = save.await_args.args[0]
        self.assertEqual(stored_entry.title, "Redis")
        self.assertEqual(stored_entry.embedding, [0.1])
        self.assertIs(save.await_args.args[1], session)

    async def test_search_embeds_query_then_delegates_to_repository(self):
        session = object()
        results = [Entry(id=3, title="Redis", content="Pub/Sub")]
        with (
            patch(
                "app.services.entry_service.generate_embedding",
                new_callable=AsyncMock,
                return_value=[0.2],
            ) as embed,
            patch(
                "app.services.entry_service.entry_repository.search_entries",
                new_callable=AsyncMock,
                return_value=results,
            ) as search,
        ):
            result = await search_entries("Redis Pub/Sub", session)

        self.assertIs(result, results)
        embed.assert_awaited_once_with("Redis Pub/Sub")
        search.assert_awaited_once_with([0.2], session)


if __name__ == "__main__":
    unittest.main()
