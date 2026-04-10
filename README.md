# DocQA Platform

> Intelligent Document Q&A — upload PDFs, ask questions, get cited answers.

[![CI](https://github.com/YOUR_USERNAME/docqa-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/docqa-platform/actions)

## Stack

**Backend:** Python 3.11, FastAPI, LangGraph, Claude API, Chroma, PostgreSQL, Redis, Celery  
**Frontend:** React 18, TypeScript, Vite, Zustand  
**Infra:** Docker, AWS ECS Fargate, GitHub Actions

## Quick start

```bash
cp backend/.env.example backend/.env
# fill in ANTHROPIC_API_KEY and SECRET_KEY
docker compose up -d
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

## Architecture

See `docs/architecture.md` (coming soon).

## Progress

- [x] Step 1: Backend foundation
- [ ] Step 2: Document ingestion pipeline
- [ ] Step 3: LangGraph agents
- [ ] Step 4: Claude function calling
- [ ] Step 5: Redis caching
- [ ] Step 6: React frontend
- [ ] Step 7: Docker full stack
- [ ] Step 8: CI/CD
- [ ] Step 9: AWS deployment
