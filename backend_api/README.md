# Backend API - Notes

This FastAPI service provides CRUD endpoints for a Notes app with SQLite persistence.

## Environment

- DB_PATH: Optional path to the SQLite database file. Defaults to `./data/notes.db`.

You may create a `.env` in the container root and set:
```
DB_PATH=./data/notes.db
```

Notes:
- The application will create the parent directory for the database path if it does not exist (e.g., `./data`).
- On startup, the service initializes the SQLite database and ensures the required schema exists (creates the `notes` table when missing).
- The DB connection uses a row factory for dict-like access and enforces `PRAGMA foreign_keys = ON`.
- Transactions auto-commit on success and rollback on error.

## CORS

This service is configured to allow browser clients running locally:
- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`, and `*` (permissive for local development).
- Allowed methods/headers: `*`
- allow_credentials: `True`

Typical frontend dev server runs on `http://localhost:3000` and will call this backend on `http://localhost:3001`.

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

### OpenAPI

- Swagger UI: `http://localhost:3001/docs`
- OpenAPI JSON: `http://localhost:3001/openapi.json`

### Regenerate OpenAPI (to file)

From the backend_api directory:
```
python -m src.api.generate_openapi
```

This writes `interfaces/openapi.json`.

## E2E Verification (from frontend)

With the frontend running on http://localhost:3000:
1. Create a note from the UI (+ button) -> POST /notes (201)
2. Edit a note -> PUT /notes/{id} (200)
3. Delete a note -> DELETE /notes/{id} (204)
4. Refresh list -> GET /notes (200)
5. Confirm no CORS errors in browser DevTools when calling http://localhost:3001 from http://localhost:3000.
