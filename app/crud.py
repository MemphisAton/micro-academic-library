from sqlalchemy.orm import Session
from . import models, schemas
import json

def create_publication(db: Session, publication: schemas.PublicationCreate):
    db_publication = models.Publication(
        **publication.dict(exclude={"tags"}),
        tags=json.dumps(publication.tags) if publication.tags else "[]"
    )
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication

def get_publications(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Publication).offset(skip).limit(limit).all()

def get_publication_by_pdf(db: Session, pdf_link: str):
    return db.query(models.Publication).filter(models.Publication.pdf_link == pdf_link).first()
