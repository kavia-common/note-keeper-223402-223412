from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from src.api.db import get_connection, iso_now
from src.api.models import Note, NoteCreate, NoteUpdate

router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


def _row_to_note(row) -> Note:
    """Convert sqlite Row to Note model."""
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[Note],
    summary="List Notes",
    description="Retrieve all notes sorted by updated_at in descending order.",
)
def list_notes():
    """Return list of notes sorted by updated_at desc."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes ORDER BY updated_at DESC"
        )
        rows = cur.fetchall()
        return [_row_to_note(r) for r in rows]


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=Note,
    summary="Get Note",
    description="Fetch a single note by its ID.",
)
def get_note(note_id: int):
    """Return a single note, or 404 if it does not exist."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return _row_to_note(row)


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    summary="Create Note",
    description="Create a new note. Title and content must be non-empty.",
)
def create_note(payload: NoteCreate):
    """Create a new note and return it."""
    title = (payload.title or "").strip()
    content = (payload.content or "").strip()
    if not title or not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title and content are required")

    now = iso_now()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, content, now, now),
        )
        note_id = cur.lastrowid
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cur.fetchone()
        return _row_to_note(row)


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=Note,
    summary="Update Note (Full)",
    description="Replace the title and content of a note.",
)
def update_note(note_id: int, payload: NoteCreate):
    """Perform a full replacement of a note's fields."""
    title = (payload.title or "").strip()
    content = (payload.content or "").strip()
    if not title or not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title and content are required")

    now = iso_now()
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

        conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (title, content, now, note_id),
        )
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cur.fetchone()
        return _row_to_note(row)


# PUBLIC_INTERFACE
@router.patch(
    "/{note_id}",
    response_model=Note,
    summary="Update Note (Partial)",
    description="Update any provided fields (title, content) for the note.",
)
def partial_update_note(note_id: int, payload: NoteUpdate):
    """Perform a partial update on the note."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        )
        existing = cur.fetchone()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

        new_title: Optional[str] = payload.title if payload.title is not None else existing["title"]
        new_content: Optional[str] = payload.content if payload.content is not None else existing["content"]
        new_title = new_title.strip() if new_title is not None else None
        new_content = new_content.strip() if new_content is not None else None

        if not new_title or not new_content:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title and content cannot be empty")

        now = iso_now()
        conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (new_title, new_content, now, note_id),
        )
        cur = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cur.fetchone()
        return _row_to_note(row)


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Note",
    description="Delete a note by its ID.",
    responses={
        204: {"description": "Note deleted"},
        404: {"description": "Note not found"},
    },
)
def delete_note(note_id: int):
    """Delete a note by ID, returning 204 on success or 404 if missing."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return None
