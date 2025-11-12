from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import init_db
from src.api.routers.notes import router as notes_router

openapi_tags = [
    {"name": "Health", "description": "Service health and status"},
    {"name": "Notes", "description": "CRUD operations for notes"},
]

app = FastAPI(
    title="Notes API",
    description="FastAPI backend for Notes CRUD with SQLite persistence.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Restrictive CORS for local dev while keeping previous permissive behavior if needed
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",  # keep existing configuration allowance as requested
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database on service startup."""
    init_db()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
)
def health_check():
    """Return service health status."""
    return {"message": "Healthy"}


# Include Notes router
app.include_router(notes_router)
