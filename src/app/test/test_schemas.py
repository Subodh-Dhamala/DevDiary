import unittest

from pydantic import ValidationError

from app.schemas import AskRequest, EntryCreate, EntryUpdate


class RequestSchemaTests(unittest.TestCase):
    def test_create_entry_trims_and_validates_text(self):
        entry = EntryCreate(title="  Redis  ", content="  Pub/Sub is ephemeral.  ")

        self.assertEqual(entry.title, "Redis")
        self.assertEqual(entry.content, "Pub/Sub is ephemeral.")

    def test_create_entry_rejects_blank_and_extra_fields(self):
        with self.assertRaises(ValidationError):
            EntryCreate(title="  ", content="A note")

        with self.assertRaises(ValidationError):
            EntryCreate(title="Redis", content="A note", unexpected="value")

    def test_update_requires_at_least_one_non_null_field(self):
        with self.assertRaises(ValidationError):
            EntryUpdate()

        with self.assertRaises(ValidationError):
            EntryUpdate(title=None, content=None)

        self.assertEqual(EntryUpdate(title="Redis").title, "Redis")

    def test_ask_question_rejects_blank_and_trims_whitespace(self):
        with self.assertRaises(ValidationError):
            AskRequest(question="  ")

        self.assertEqual(AskRequest(question="  What did I save? ").question,
                         "What did I save?")


if __name__ == "__main__":
    unittest.main()
