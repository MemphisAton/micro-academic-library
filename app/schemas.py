from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class PublicationBase(BaseModel):
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
    pass

class PublicationOut(PublicationBase):
    id: int
    created_at: datetime
    tags: List[str]  # важно: именно список, не Optional

    class Config:
        orm_mode = True