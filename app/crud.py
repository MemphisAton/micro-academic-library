import json

from sqlalchemy.orm import Session

from . import models, schemas


def create_publication(db: Session, publication: schemas.PublicationCreate):
    """Create a new publication in the database."""
    db_publication = models.Publication(
        **publication.dict(exclude={"tags"}),
        tags=json.dumps(publication.tags) if publication.tags else "[]"
    )
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication


def get_publications(db: Session, skip: int = 0, limit: int = 20):
    """Return a list of publications with optional pagination."""
    return db.query(models.Publication).offset(skip).limit(limit).all()


def get_publication_by_pdf(db: Session, pdf_link: str):
    """Return a publication by its PDF link if it exists."""
    return db.query(models.Publication).filter(models.Publication.pdf_link == pdf_link).first()
