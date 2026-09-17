# Backend — KOHLER AI Bathroom Intelligence

Engine 1 is the authoritative catalogue access layer. It does **not** make design decisions.

## Responsibilities

- Ingest the structured KOHLER India Price Book dataset.
- Preserve SKU, price, dimensions, specifications, relationships and provenance.
- Keep catalogue review flags visible; never silently invent missing facts.
- Expose deterministic product and relationship queries for later engines.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas for controlled CSV ingestion

## Run

Set `DATABASE_URL`, install `requirements.txt`, then from `backend/`:

```bash
python -m scripts.import_catalogue --replace
uvicorn app.main:app --reload
```

API documentation is available at `/docs` when the server is running.

## Architecture boundary

```text
Price Book CSV
    ↓
Validation + normalization
    ↓
PostgreSQL
    ↓
Engine 1 repository/API
    ↓
Engine 2 retrieval
    ↓
Engine 3 constraints + optimization
```

Engine 2 and later engines must consume this repository/API rather than reading the CSV directly.
