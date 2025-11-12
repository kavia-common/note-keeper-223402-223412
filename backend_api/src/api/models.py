from typing import Optional
from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base model containing common note fields."""
    title: Optional[str] = Field(default=None, description="Title of the note")
    content: Optional[str] = Field(default=None, description="Content/body of the note")


class NoteCreate(NoteBase):
    """Model for creating a note. Requires non-empty title and content."""
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content/body of the note")


class NoteUpdate(NoteBase):
    """Model for partial or full update of a note. All fields optional."""
    pass


class Note(NoteBase):
    """Full Note representation including identifiers and timestamps."""
    id: int = Field(..., description="Unique identifier of the note")
    created_at: str = Field(..., description="Creation timestamp in ISO8601")
    updated_at: str = Field(..., description="Last update timestamp in ISO8601")
