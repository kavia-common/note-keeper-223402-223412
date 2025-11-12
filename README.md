# note-keeper-223402-223412

This workspace contains:
- backend_api: FastAPI service exposing Notes CRUD with SQLite.

Run summary:
1) `cd backend_api && pip install -r requirements.txt`
2) Optional: `export DB_PATH=./data/notes.db`
3) Start: `uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001`
4) Swagger UI: http://localhost:3001/docs
5) OpenAPI JSON: http://localhost:3001/openapi.json
6) Regenerate spec file: `python -m src.api.generate_openapi` → writes `interfaces/openapi.json`

CORS:
- Allows http://localhost:3000 and http://127.0.0.1:3000 (and `*` for local convenience)
- This enables the React frontend at port 3000 to call the backend at port 3001

See backend_api/README.md for details and E2E verification steps.