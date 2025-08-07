from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from threading import Thread
from app.database import SessionLocal
from scripts.downloader_arxiv import fetch_arxiv_papers
from scripts.extractor_ai import extract_metadata_from_pdf
from . import crud, schemas
from . import schemas, crud
from .database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/publications/", response_model=List[schemas.PublicationOut])
async def list_publications(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    pubs = crud.get_publications(db, skip=skip, limit=limit)
    return [
        schemas.PublicationOut(
            **{k: v for k, v in pub.__dict__.items() if k != "tags"},
            tags=pub.tags_list
        )
        for pub in pubs
    ]

@router.post("/publications/bulk/arxiv/")
async def bulk_add_from_arxiv(limit: int = 100):
    Thread(target=background_arxiv_loader, args=(limit,), daemon=True).start()
    return {"status": "started", "message": f"Начата фоновая загрузка {limit} публикаций из arXiv"}



def background_arxiv_loader(limit: int):
    from scripts.downloader_arxiv import fetch_arxiv_papers
    from scripts.extractor_ai import extract_metadata_from_pdf
    from app.database import SessionLocal
    from app import crud, schemas
    import requests

    db = SessionLocal()
    papers = fetch_arxiv_papers(limit=limit)
    for paper in papers:
        try:
            if crud.get_publication_by_pdf(db, paper["pdf_link"]):
                continue

            pdf_response = requests.get(paper["pdf_link"], timeout=20)
            pdf_response.raise_for_status()
            pdf_bytes = pdf_response.content

            extracted = extract_metadata_from_pdf(pdf_bytes)
            if not extracted:
                continue

            combined = {**paper, **extracted}

            if isinstance(combined.get("tags"), str):
                combined["tags"] = [combined["tags"]]
            if not isinstance(combined.get("tags"), list):
                combined["tags"] = []

            for field in ["language", "organization", "country"]:
                value = combined.get(field)
                if isinstance(value, list):
                    combined[field] = ", ".join(value)
                elif value is None:
                    combined[field] = ""

            crud.create_publication(db, schemas.PublicationCreate(**combined))
        except Exception as e:
            print(f"❌ Error for {paper['pdf_link']}: {e}")
            continue
    db.close()