import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base


class Publication(Base):
    """SQLAlchemy model for a scientific publication."""
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    tags = Column(Text)
    year = Column(Integer)
    organization = Column(String)
    country = Column(String)
    language = Column(String)
    pdf_link = Column(Text, nullable=False)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tags_list(self):
        """Return tags as a list parsed from JSON string."""
        try:
            return json.loads(self.tags)
        except Exception:
            return []
