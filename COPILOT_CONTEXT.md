# Project: DocQA Platform — Copilot Session Context

## Who I am

AI Engineer / Full-Stack SWE at JPMorgan Chase. MS CS, Texas Tech (May 2025).
I write production-quality code, not tutorials. I will push back if suggestions are naive.

## Project summary

Full-stack Intelligent Document Q&A Platform. Users upload PDFs, ask questions in
natural language, get answers with source citations. Agentic backend using LangGraph
multi-agent orchestration + RAG pipeline + Claude API.

## Tech stack (non-negotiable)

Backend: Python 3.11, FastAPI, SQLAlchemy 2.0 async, Alembic, Celery, Pydantic v2
AI: Claude API (claude-sonnet-4-5), LangGraph, Chroma vector DB, voyage-3 embeddings
Data: PostgreSQL (asyncpg), Redis (cache + Celery broker)
Storage: AWS S3
Frontend: React 18, TypeScript, Vite, Zustand, Axios
Infra: Docker, AWS ECS Fargate, GitHub Actions CI/CD

## Code standards (always enforce these)

- Async everywhere in FastAPI (async def, await, asyncpg, aioredis)
- Pydantic v2 models for all request/response schemas
- SQLAlchemy 2.0 style: Mapped[], mapped_column(), not Column()
- Typed everything: no `Any` unless unavoidable, no untyped dicts
- Structured logging with structlog, not print() or bare logging
- Services layer owns business logic, routes only validate and delegate
- Agents own AI orchestration, services call agents
- Error handling: custom exception classes, never bare `except Exception`
- Tests: pytest-asyncio, factory-boy for fixtures, aim for 80%+ coverage

## Architecture layers (respect this separation)

routes (api/v1/) → services/ → agents/ → external APIs
routes never call agents directly
services never import from api/

## Current build status

[UPDATE THIS SECTION each session]

- Step 1 DONE: FastAPI app factory, config, database, ORM models, Alembic migrations
- Step 2 IN PROGRESS: Document ingestion pipeline
- Step 3 TODO: LangGraph agents
- Step 4 TODO: Claude function calling + citations
- Step 5 TODO: Redis caching
- Step 6 TODO: React frontend
- Step 7 TODO: Docker Compose full stack
- Step 8 TODO: GitHub Actions CI/CD
- Step 9 TODO: AWS ECS deployment

## File structure (do not deviate)

docqa-platform/
backend/
app/
api/v1/ # routes only
agents/ # LangGraph graphs
core/ # config, db, redis, security
models/ # SQLAlchemy ORM
schemas/ # Pydantic v2
services/ # business logic
tasks/ # Celery tasks
alembic/
tests/
frontend/
src/
components/
hooks/
stores/
api/
types/
infra/
docker/
aws/
.github/workflows/

## Key decisions already made (do not re-suggest alternatives)

- Chroma for vector DB (not Pinecone, not Weaviate)
- Celery + Redis for async doc processing (not background tasks)
- LangGraph for agent orchestration (not plain LangChain)
- voyage-3 for embeddings via Anthropic (not OpenAI)
- Zustand for frontend state (not Redux, not Context)
- asyncpg driver (not psycopg2)

## What I expect from every response

1. Complete, runnable code — no placeholders like `# TODO implement this`
2. Type hints on every function signature
3. Docstrings on public methods (one-line is fine)
4. If you suggest a library, it must already be in pyproject.toml
5. If a new dependency is needed, say so explicitly and give the pip install command
6. Explain non-obvious decisions in a short comment, not a paragraph
7. When writing tests, use async fixtures and real assertions, not just `assert True`
