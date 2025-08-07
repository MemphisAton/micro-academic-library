from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.types import JSON
from datetime import datetime
from .database import Base

import json

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    tags = Column(Text)  # храним как JSON-строку
    year = Column(Integer)
    organization = Column(String)
    country = Column(String)
    language = Column(String)
    pdf_link = Column(Text, nullable=False)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tags_list(self):
        try:
            return json.loads(self.tags)
        except Exception:
            return []
