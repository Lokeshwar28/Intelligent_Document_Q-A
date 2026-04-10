# Build progress

## Done

- [x] Step 1: FastAPI foundation, models, migrations

## In progress

- [ ] Step 2: Document ingestion (S3 + Celery + chunker + Chroma)
  - [x] S3 upload helper
  - [ ] Celery task
  - [ ] PyMuPDF parser
  - [ ] Chunker + embedder
  - [ ] Chroma upsert

## Blocked on

- nothing

## Decisions log

- Chose Chroma over Pinecone: simpler local dev, no account needed
- voyage-3 over text-embedding-3: staying in Anthropic ecosystem
