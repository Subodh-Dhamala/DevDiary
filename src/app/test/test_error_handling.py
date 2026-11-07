import unittest

from starlette.requests import Request

from app.main import handle_unexpected_error


class ErrorHandlingTests(unittest.IsolatedAsyncioTestCase):
    async def test_unexpected_errors_return_generic_server_error(self):
        request = Request(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": "/api/v1/entries",
                "raw_path": b"/api/v1/entries",
                "query_string": b"",
                "headers": [],
                "server": ("testserver", 80),
                "client": ("127.0.0.1", 12345),
            }
        )
        error = RuntimeError("sensitive internal details")

        with self.assertLogs("app.main", level="ERROR"):
            response = await handle_unexpected_error(request, error)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.body, b'{"detail":"Internal server error"}')
        self.assertNotIn(b"sensitive internal details", response.body)


if __name__ == "__main__":
    unittest.main()
