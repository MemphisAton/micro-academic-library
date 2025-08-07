from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PublicationBase(BaseModel):
    """Base schema for a publication (shared fields)."""
    title: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = []
    year: Optional[int] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    pdf_link: str
    source: Optional[str] = None


class PublicationCreate(PublicationBase):
    """Schema for creating a new publication."""
    pass


class PublicationOut(PublicationBase):
    """Schema for returning a publication from the database."""
    id: int
    created_at: datetime
    tags: List[str]

    class Config:
        orm_mode = True
