# DevDiary

DevDiary is an API for saving developer notes, searching them by meaning, and
asking a Gemini-powered assistant questions about them. Notes are stored in
PostgreSQL, with embeddings indexed as pgvector values.

## Features

- Create, list, retrieve, update, and delete notes.
- Generate an embedding whenever a note is created or edited.
- Search notes with cosine similarity.
- Ask an assistant to search saved notes or, when permitted and explicitly
  asked, save a note.
- Explore the API through FastAPI's Swagger UI.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for the included PostgreSQL/pgvector service)
- A Gemini API key

## Run locally

Run these commands from the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace `GEMINI_API_KEY` with your key. The example uses
`localhost:5433` for PostgreSQL, matching the port Docker Compose publishes.
The values in the example are for local development; change the database
credentials before using this setup in a shared or production environment.

Start the database, install the locked dependencies, apply migrations, then
start the API:

```powershell
docker compose up -d db
uv sync --frozen
uv run alembic upgrade head
uv run uvicorn app.main:app --app-dir src --reload
```

The API listens on `http://localhost:8000`. Open
[Swagger UI](http://localhost:8000/docs) to try the endpoints, or
[ReDoc](http://localhost:8000/redoc) to browse the generated API reference.

`GET /health` checks that the web process is responding. It does not check
database connectivity.

## Run the full stack with Docker Compose

Create and configure `.env` as described above, then run:

```powershell
docker compose up --build
```

Compose starts PostgreSQL, waits for its health check, builds the API image,
runs database migrations, and starts Uvicorn. Swagger UI is available at
[http://localhost:8000/docs](http://localhost:8000/docs).

Stop the containers with `docker compose down`. The named database volume is
kept, so notes remain when you bring the stack back up. To remove the database
volume and its data as well, run `docker compose down -v`.

## Configuration

`src/app/config.py` loads settings from environment variables and `.env` using
`pydantic-settings`. The Gemini key is represented as a `SecretStr`.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async SQLAlchemy connection string used by the app and Alembic. |
| `GEMINI_API_KEY` | Yes | API key for Gemini generation and embeddings. |
| `DATABASE_ECHO` | No | Set to `true` to log SQL statements; defaults to `false`. |
| `LOG_LEVEL` | No | Python log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. |
| `DATABASE_URL_DOCKER` | No | Compose interpolation value for the API-to-database URL; defaults to the Compose database service. |
| `POSTGRES_USER` | No | PostgreSQL container user; local default is `devdiary`. |
| `POSTGRES_PASSWORD` | No | PostgreSQL container password; local default is `devdiary123`. Change it outside local development. |
| `POSTGRES_DB` | No | PostgreSQL database name; local default is `devdiary`. |

Use the host database URL while running the app on your computer. When the API
runs inside Compose, it connects to the `db` service on the Docker network.
Keep `.env` private; only `.env.example` belongs in version control.

## API

Entry endpoints are prefixed with `/api/v1`. Requests and responses use JSON,
except for endpoints with query parameters. Every route is also listed in
Swagger UI at `/docs`.

### Assistant

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/entries/ask?question=...` | Ask a read-only question. The assistant may search notes but cannot save through its tool. |
| `POST /api/v1/entries/ask` | Ask a question with search and save tools available. Saving should only happen when explicitly requested. |

Both routes return a response in this shape:

```json
{
  "question": "What did I save about Redis?",
  "answer": "Your saved notes say ...",
  "sources": [
    {"id": 12, "title": "Redis"}
  ]
}
```

`sources` contains the notes returned by search; it is empty when no search was
used or no notes matched.

Read-only example:

```http
GET /api/v1/entries/ask?question=What%20did%20I%20save%20about%20Redis%3F
```

Assistant request with saving enabled:

```http
POST /api/v1/entries/ask
Content-Type: application/json

{
  "question": "Remember that I prefer Redis for caching."
}
```

The POST route does not save every question. Gemini chooses whether to request
one of the tools based on the question and tool descriptions. For direct note
creation without the assistant, use `POST /api/v1/entries`.

### Note management and search

| Method and path | Input | Success response |
| --- | --- | --- |
| `GET /health` | None | `200`; `{"status": "ok"}` when the API process is responding. |
| `POST /api/v1/entries` | JSON `{"title": "...", "content": "..."}` | `201`; the created entry. |
| `GET /api/v1/entries` | None | `200`; an array of entries. |
| `GET /api/v1/entries/{entry_id}` | Positive integer path parameter | `200`; one entry. |
| `PATCH /api/v1/entries/{entry_id}` | JSON containing `title`, `content`, or both | `200`; the updated entry. |
| `DELETE /api/v1/entries/{entry_id}` | Positive integer path parameter | `204`; no response body. |
| `GET /api/v1/entries/search?query=...` | Search text | `200`; an array of matching entries. |

Example create request:

```http
POST /api/v1/entries
Content-Type: application/json

{
  "title": "Redis caching",
  "content": "I prefer Redis for caching."
}
```

Example semantic search:

```http
GET /api/v1/entries/search?query=Redis%20caching
```

Search embeds the query and returns at most five entries with cosine distance
below `0.3`, ordered by distance. An empty array means no entry met that
threshold.

Entry titles must be 1–255 characters and content must be 1–50,000 characters.
Ask requests are limited to 4,000 characters and search queries to 1,000.
Whitespace is trimmed and blank values are rejected. PATCH requests must
include at least one non-null field. Unknown JSON fields are rejected.

Entry responses include the generated embedding as well as the note fields.
Embeddings are 1,536-dimensional vectors; they can make response bodies large.


## How assistant requests work

The ask endpoints use a hand-written tool-calling loop. Gemini chooses whether
to answer directly or ask the application to call a tool. Gemini never connects
to the database itself.

```text
HTTP route
  -> rag_service.ask_question
  -> Gemini receives the question and available tool descriptions
       -> answer text: return answer
       -> function call: validate and execute tool
            -> search: embed query -> vector search -> return notes
            -> save: validate note -> embed note -> persist it
          send tool result back to Gemini
          repeat until Gemini returns an answer (maximum 3 tool rounds)
  -> return answer and search sources to caller
```

The tool schemas live in `src/app/services/tool_definitions.py`. The execution
and argument validation are in `src/app/services/tool_executor.py`. The
orchestration loop and round limit are in
`src/app/services/rag_service.py`. Model calls are sent from
`src/app/services/generation_service.py`.

For searching, the entry service asks Gemini's embedding model to turn the
query into a vector. The repository uses pgvector's cosine distance to find
matching entries. For saving, the same embedding process runs on the title and
content before the entry is written.

## Project layout

```text
migrations/                 Alembic environment and schema revisions
src/app/
  main.py                   FastAPI app, logging, error handling, health route
  config.py                 Validated environment settings
  database.py               SQLAlchemy engine and request-scoped sessions
  schemas.py                Request validation and response models
  models/                   SQLAlchemy table definitions
  routes/                   HTTP endpoints
  services/                 Application and Gemini logic
  repositories/             Database queries and transaction commits
  test/                     Unit tests and optional live-check scripts
Dockerfile                  Multi-stage API image
docker-compose.yml          PostgreSQL and API services
```

The main code path is **route → service → repository**. Routes handle HTTP,
services implement application behavior, and repositories handle SQLAlchemy
queries and commits. The embedding and text-generation services make requests
to Gemini.

## Database migrations

The initial migration creates the entries table and enables the PostgreSQL
`vector` extension. Alembic reads `DATABASE_URL`, the same setting as the
application.

After changing a SQLAlchemy model, generate a revision, inspect the generated
file, then apply it:

```powershell
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

Useful commands:

```powershell
uv run alembic current
uv run alembic history
uv run alembic downgrade -1
```

Do not edit a migration that has already been applied to a shared database.
Create a new revision instead.

## Tests

Run the unit tests from the repository root:

```powershell
uv run python -m unittest discover -s src\app\test -p "test_*.py"
```

The unit tests use mocks for Gemini and database operations where appropriate.
`test_db.py`, `test_embedding.py`, `test_generation.py`, and
`test_function_calling.py` are standalone live-check scripts; run them
individually when you want to contact the configured database or Gemini API.

## Operational notes

- Request logs include method, path, status, and elapsed time. Do not add note
  contents, API keys, or other sensitive values to logs.
- SQL statement logging is off by default. Enable `DATABASE_ECHO=true` only
  when debugging locally.
- The `/health` endpoint reports that the API process is serving requests; it
  is not a readiness check for PostgreSQL or Gemini.
- The Compose database port is published on host port `5433`; the API listens
  on host port `8000`.