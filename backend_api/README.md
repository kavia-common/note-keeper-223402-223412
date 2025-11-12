# Backend API - Notes

This FastAPI service provides CRUD endpoints for a Notes app with SQLite persistence.

## Environment

- DB_PATH: Optional path to the SQLite database file. Defaults to `./data/notes.db`.

You may create a `.env` in the container root and set:
```
DB_PATH=./data/notes.db
```

Note: Do not commit secrets; DB_PATH is safe to configure per environment. The application ensures the `./data` directory exists.

## Run locally

1. Install dependencies (if not already):
```
pip install -r requirements.txt
```

2. Start the server:
```
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
```

On startup, the service will initialize the SQLite DB and the `notes` table if missing.

## API

- Health Check: `GET /`
- Notes CRUD:
  - `GET /notes`
  - `GET /notes/{note_id}`
  - `POST /notes`
  - `PUT /notes/{note_id}`
  - `PATCH /notes/{note_id}`
  - `DELETE /notes/{note_id}`

All timestamps are ISO8601 (UTC).

## Regenerate OpenAPI

From the backend_api directory:
```
python -m src.api.generate_openapi
```

This writes `interfaces/openapi.json`.
