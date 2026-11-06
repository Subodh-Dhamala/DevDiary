# DevVault — Learn-While-Building Roadmap

A step-by-step plan to learn backend + AI engineering by building "DevVault," a developer-notes app with semantic search, RAG, and function calling.

**Adjusted for you:** you already know Python and have Node backend experience, so this skips language fundamentals and focuses on what's new — FastAPI's specific patterns, then straight into DB/AI work, with the "why," not just the "what," for each concept.

**How to use this:** Work top to bottom. Don't skip ahead. Each phase has: what to learn, *why it matters*, resources, a hands-on exercise, common pitfalls, and a goal checkpoint. Don't move on until the goal actually works.

---

## Before You Start

- Estimated total time: **6–10 weeks** at ~5–8 hrs/week
- Tools to install now: Python 3.11+, `uv` (or `pip`), PostgreSQL, Docker, a code editor, an LLM API key (OpenAI or Anthropic)
- Keep a running `NOTES.md` — write each new concept in your own words. This is more valuable than the code itself.
- Mental model shortcut: FastAPI ≈ Express with type-enforced request/response bodies (Pydantic) baked in, native async support, and auto-generated docs (`/docs`).

---

## Phase 0 — FastAPI-Specific Setup (Est. 1 day)

### What to learn
- `uv` (or `pip`) project setup — Python's rough equivalent of `npm init` + `package.json`
- `.env` handling via `python-dotenv` or `pydantic-settings`
- FastAPI project layout conventions (`app/main.py`, routers, dependency modules — think Express's `routes/`, `middleware/`)
- How FastAPI's async differs from Node's event loop

### Why it matters
Node's ecosystem makes almost everything async-by-default (most I/O libraries return promises). Python doesn't — a blocking call (like a synchronous DB driver) inside an `async def` route will stall FastAPI's *entire* event loop, not just that request. This trips up Node devs constantly, so get it early.

### Resources
- FastAPI official docs → "First Steps" and "Bigger Applications" pages (the routers section maps directly to how you'd split Express routes into files)
- `uv` docs "Getting Started" — 10 minute read, replaces needing pip/venv knowledge

### Exercise
Scaffold a project with `uv init`, add FastAPI + Uvicorn, create one `GET /health` route, run it, and open `/docs` — compare the auto-generated Swagger UI to how you'd normally document an Express API by hand.

### Common pitfalls
- Forgetting `async def` vs `def` matters: FastAPI runs `def` routes in a thread pool, `async def` on the event loop. Mixing them wrong causes subtle slowdowns.
- Using `time.sleep()` instead of `asyncio.sleep()` inside async routes (blocks everything).

### Goal
✅ Run a bare FastAPI server locally, hit `/docs`, see the auto-generated OpenAPI UI.

---

## Phase 1 — FastAPI Basics (Est. 4–6 days)

### Build
```
POST   /notes
GET    /notes
GET    /notes/{id}
DELETE /notes/{id}
```

### What to learn
- FastAPI routing (`@app.get`, `@app.post`) — decorator-based, unlike Express's `router.get(path, handler)`
- Pydantic models for request/response validation — Python's equivalent of Zod/Joi, but the model *is* your data class too
- Path params, query params, request bodies, and how FastAPI infers which is which from function signatures
- Dependency injection (`Depends`) — closest Node parallel is Express middleware, but scoped per-route rather than global-by-default
- Error handling (`HTTPException`, status codes)

### Why it matters
This is the biggest conceptual shift from Express: instead of manually validating `req.body` with a schema library and passing it along, Pydantic validation is baked into the function signature. If the request doesn't match the type, FastAPI auto-rejects it with a 422 before your code even runs.

### Resources
- FastAPI docs: "Path Parameters," "Query Parameters," "Request Body," "Dependencies" (read in that order — each builds on the last)
- Pydantic docs: "Models" page — just enough to define nested/optional fields

### Exercise
Build the four endpoints above using an in-memory list first (no DB yet). Then add a `Depends`-based function that validates an API key header on every route — this is your first taste of DI replacing Express middleware.

### Common pitfalls
- Trying to access `request.body` manually like Express — in FastAPI you just declare a Pydantic model as a parameter and it's parsed for you.
- Forgetting response models (`response_model=...`) — without it, FastAPI will happily leak fields you didn't mean to expose (e.g., internal-only fields).

### Goal
✅ A working REST API you can fully exercise from `/docs` without writing a separate client.

---

## Phase 2 — PostgreSQL (Est. 1–1.5 weeks)

### Build
Replace in-memory storage with a real `notes` table.
```
notes
-----
id
content
created_at
```

### What to learn
- SQLAlchemy ORM basics (engine, session, declarative models) — think Prisma/Sequelize, but more explicit about sessions
- Database sessions and connection lifecycle (opening/closing per request via `Depends`)
- Alembic migrations — Python's equivalent of Prisma Migrate / Knex migrations
- CRUD wired to your Phase 1 endpoints

### Why it matters
SQLAlchemy's session model is stricter than most Node ORMs about transaction boundaries — you explicitly `commit()` or `rollback()`. This forces you to actually understand what a transaction is, which most ORM abstractions hide.

### Resources
- SQLAlchemy 2.0 docs: "ORM Quick Start" (use 2.0-style syntax, not the older 1.x style — most tutorials online are outdated)
- Alembic docs: "Tutorial" page — just the autogenerate + upgrade/downgrade workflow
- FastAPI docs: "SQL (Relational) Databases" page — shows the exact session-per-request pattern you'll use

### Exercise
Set up Postgres in Docker, connect via SQLAlchemy, generate your first Alembic migration for the `notes` table, then rewire your Phase 1 endpoints to read/write real rows.

### Common pitfalls
- Sharing one global DB session across requests (causes race conditions) — use `Depends` to get a fresh session per request.
- Forgetting to run `alembic upgrade head` after generating a migration — the migration file existing doesn't mean it ran.

### Goal
✅ `POST /notes` → FastAPI → PostgreSQL, and data persists across server restarts.

---

## Phase 3 — First LLM Integration (Est. 2–4 days)

### Build
```
POST /ai/ask
Input: { "question": "Explain Redis Pub/Sub" }
```

### What to learn
- Calling an LLM API from a backend (raw HTTP or official SDK)
- API key management (never hardcode, always `.env`)
- System prompts vs. user prompts — what each is *for*
- Reading model responses (text vs. structured/tool-call content)
- Token counting and cost awareness (input tokens + output tokens = price)

### Why it matters
This is the smallest phase on purpose — the goal is to strip away every later abstraction (RAG, tools, agents) and see that an "AI feature" is fundamentally just an HTTP call with a prompt in and text out. Everything after this phase is about making that prompt smarter.

### Resources
- Anthropic API docs: "Messages" quickstart, and the "Prompt engineering overview" for how system vs. user prompts behave differently
- Whichever provider's SDK docs (Python) — install, auth, first call

### Exercise
Hit your `/ai/ask` endpoint with a few different system prompts for the *same* question (e.g., "answer in one sentence" vs. "answer like a senior engineer explaining to a junior") and note how much the output changes. This builds intuition before you start doing real prompt engineering in Phase 6.

### Common pitfalls
- Putting instructions meant for the model into the user prompt instead of the system prompt (works, but muddies later prompt engineering).
- Not handling API errors/timeouts — LLM calls fail more often than typical REST calls; wrap them properly.

### Goal
✅ You can explain, without hand-waving, exactly what happens between your endpoint receiving a question and returning an answer.

---

## Phase 4 — Embeddings (Est. 3–5 days, mostly conceptual)

### Build
When a note is created, generate its embedding.
```
Note → Embedding model → Vector → Database
```

### What to learn
- What embeddings are: a vector (list of numbers) representing meaning, produced by a model trained so that similar meanings land close together in that vector space
- Dimensions (why 384, 768, 1536 — different embedding models output different-sized vectors; you can't mix them)
- Cosine similarity, dot product, Euclidean distance — the three common ways to measure "closeness" between vectors
- Why embeddings beat keyword search for meaning ("cache eviction" should match a note about "removing old entries from Redis" even with zero shared words)

### Why it matters
This phase is 90% conceptual and 10% code — one API call to get an embedding. Understanding *why* it works matters more than the code, because you'll be debugging "why didn't my search find this note" later, and the answer is almost always something about how embeddings/similarity work, not a bug.

### Resources
- OpenAI's "Embeddings" guide (concept explanation is provider-agnostic even if you use a different model)
- A short intuition-builder: search "embedding projector tensorflow" and play with the interactive visualization — seeing words cluster in 3D makes the abstract concept click fast

### Exercise
Generate embeddings for 5 short unrelated sentences and 5 sentences that are paraphrases of each other. Manually compute cosine similarity between all pairs (a 5-line Python script with `numpy`) and confirm the paraphrases score higher.

### Common pitfalls
- Assuming embeddings capture exact keyword matches well — they're actually often *worse* at exact terms (e.g., a specific function name) than plain text search. Real systems often combine both (hybrid search) — worth knowing even if DevVault doesn't implement it.

### Goal
✅ You can explain embeddings to someone else without hand-waving, and you've seen similarity scores with your own eyes.

---

## Phase 5 — pgvector (Est. 1 week)

### Build
Add a vector column to `notes` and store embeddings there.
```
User question → Question embedding → pgvector similarity search → Top relevant notes
```

### What to learn
- Installing/enabling the `pgvector` extension in Postgres
- Vector column types (`vector(1536)` etc. — must match your embedding model's dimension)
- Similarity search queries (`<->` for L2 distance, `<=>` for cosine distance)
- Basic indexing (IVFFlat / HNSW) — what they trade off (build time / accuracy / speed) at a conceptual level, not deep tuning

### Why it matters
This is where "AI feature" and "regular backend skills" merge — you're just writing SQL, but the SQL is doing semantic search. No new framework, no vector database service needed for a project this size; that's the point pgvector proves.

### Resources
- pgvector GitHub README — genuinely the best doc, it's short and has copy-pasteable SQL
- SQLAlchemy + pgvector integration: search "pgvector-python sqlalchemy example" for the ORM-side setup

### Exercise
Store embeddings for ~10 notes on different topics, then write one query that takes a new question's embedding and returns the top 3 closest notes. Manually sanity-check the results make sense.

### Common pitfalls
- Dimension mismatch errors (your column dimension must exactly match the embedding model's output size).
- Forgetting an index on a small dataset isn't a problem — but not understanding *why* you'd need one at scale will bite you if asked about it later.

### Goal
✅ Semantic search works — searching "cache invalidation" returns notes about Redis even without that exact phrase.

---

## Phase 6 — RAG (Est. 1.5–2 weeks)

### Build
```
Question → Embedding → Vector search → Relevant notes → Prompt + context → LLM → Answer
```
This is DevVault's core AI feature.

### What to learn
- Retrieval strategies (top-k, similarity thresholds — when to include vs. exclude a "relevant" note)
- Context injection into prompts (how you literally paste retrieved notes into the system/user prompt)
- Prompt construction patterns for RAG (a common structure: instructions → retrieved context → question)
- Chunking strategies (splitting long notes so retrieval is precise, not "here's an entire document")
- Relevance vs. noise (too much retrieved context confuses the model as much as too little)
- Hallucination — why it happens, and how grounding in retrieved context reduces (not eliminates) it
- Citing sources back to the user (returning which notes were used)

### Why it matters
RAG is the single most in-demand AI-integration pattern right now, and it's also the phase where most tutorials wave their hands. Building it manually — no LangChain — means you actually understand every moving part when you inevitably have to debug "why is the answer wrong" in a real job.

### Resources
- Anthropic's "Contextual retrieval" blog post (goes into chunking + retrieval quality)
- Pinecone's "What is RAG" guide (vendor-agnostic despite being a vector DB company, good diagrams)

### Exercise
Deliberately break it: ask a question with no relevant notes stored, and see how the model behaves. Then improve your prompt to explicitly say "if the context doesn't contain the answer, say you don't know" and compare the difference. This one exercise teaches more about grounding than reading five articles.

### Common pitfalls
- Not truncating/limiting how many notes get injected — costs balloon and quality often drops with too much context.
- Forgetting to tell the model in the system prompt to *only* use the provided context — without that instruction it'll blend in outside knowledge, defeating the point.

### Goal
✅ Ask a question, get an answer grounded in your own notes, with visible sources, and it visibly says "I don't know" when nothing relevant exists.

---

## Phase 7 — Function Calling (Est. 1–1.5 weeks)

### Build two tools
```
search_notes()
save_note()
```

### What to learn
- Tool/function schemas (how you describe available functions so the model knows they exist and what params they take)
- How the model decides to call a tool vs. answer directly
- Handling tool calls: parsing the model's request, running your actual function, returning the result back to the model
- Multi-step (agentic) LLM workflows — a full round trip: model requests tool → you execute → you send result back → model gives final answer

### Why it matters
This is conceptually the biggest jump so far: the model isn't just generating text anymore, it's making decisions about *what code to run*. Understanding this loop is the foundation for literally every "AI agent" product you'll encounter afterward.

### Resources
- Anthropic docs: "Tool use" overview and "How to implement tool use"
- Read one real schema example closely — pay attention to how the `description` fields are what the model actually reads to decide when to call a tool (bad descriptions = bad tool selection)

### Exercise
Give the model both tools and a question that requires *neither* (like "what's 2+2") and confirm it answers directly without calling anything. Then ask something that clearly needs `search_notes()`. Watching it correctly choose is the "aha" moment for this phase.

### Common pitfalls
- Vague tool descriptions — the model picks tools based on the description text, so "search notes" vs. "search the user's saved developer notes by semantic similarity to find relevant past entries" makes a real difference.
- Not validating the model's tool-call arguments before executing them (treat them like any other untrusted input).

### Goal
✅ "What did I write about Redis?" correctly triggers `search_notes()`; "Remember that Redis Pub/Sub doesn't persist messages" correctly triggers `save_note()`.

---

## Phase 8 — Intelligent Workflow (Est. 1 week)

Don't reach for LangChain or an agent framework yet — build the routing logic by hand first.

```
User question → LLM → (Answer directly) OR (Search notes → Relevant notes → LLM → Answer)
```

### What to learn
- How the LLM decides which branch to take, and how your code reads that decision
- Why building this manually matters before adopting a framework
- What an "agent" actually is, stripped of marketing language: a loop where a model's output determines the next code that runs

### Why it matters
Once you've built this loop yourself, LangChain/agent frameworks stop being magic and become "oh, this just wraps the loop I already wrote, with more config." That's a genuinely valuable interview talking point.

### Resources
- No framework docs needed here on purpose — this phase is about writing the `if tool_call: ... else: ...` loop yourself
- If you want a sanity check afterward, skim LangChain's "AgentExecutor" source/docs and see how closely it resembles what you built

### Exercise
Log every step of the loop to your console (question in → model decision → tool executed (if any) → final answer) so you can literally watch the decision-making happen in real time.

### Common pitfalls
- Infinite tool-call loops if you don't cap the number of round trips — always set a max-iterations guard.

### Goal
✅ You could explain to a colleague exactly what a framework like LangChain automates, because you built the core loop by hand first.

---

## Phase 9 — Clean It Up (Est. 1 week)

Only start once the AI functionality fully works end to end.

### What to do
- [ ] Separate routes / services / repositories (mirrors how you'd already structure a larger Express app)
- [ ] Centralized error handling
- [ ] Input validation everywhere (not just the happy path)
- [ ] Logging
- [ ] Finalize database migrations
- [ ] `.env` + config management via `pydantic-settings`
- [ ] README with setup instructions
- [ ] Dockerize the app (multi-stage build: install deps → copy app → run uvicorn)

### Resources
- FastAPI docs: "Deployment" section for production-readiness basics (workers, uvicorn vs. gunicorn+uvicorn)

### Goal
✅ DevVault is something you could show in an interview or portfolio without embarrassment — someone else could clone it, follow the README, and run it.

---

## The Learning Order (Quick Reference)

```
FastAPI setup → FastAPI basics → PostgreSQL → LLM API → Embeddings
   → pgvector → RAG → Function calling → AI workflow → Docker/cleanup
```

## What You'll Be Able to Say After This

Not: *"I used the ChatGPT API."*

Instead: *"I built a FastAPI backend that stores developer notes in PostgreSQL, generates embeddings for semantic retrieval using pgvector, uses RAG to provide relevant context to an LLM, and implements function calling so the model can search and save notes."*

That statement directly maps to an **AI & LLM Integration** skillset on a resume or in an interview.

---

## Tips for Staying on Track

1. **Don't skip the goal checkpoint** at the end of each phase — if it's not working, you're not ready for the next one.
2. **Do the exercises, not just the build.** They're designed to build intuition the main build won't give you on its own.
3. **Resist framework shortcuts** until Phase 8 is done manually.
4. **If you get stuck for >1 hour**, that's a good sign you found something worth deeply learning — search for the specific error, not the whole feature.
