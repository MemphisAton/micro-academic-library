from datetime import datetime
from threading import Thread
from typing import List

import requests
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import SessionLocal
from scripts.downloader_arxiv import fetch_arxiv_papers
from scripts.extractor_ai import extract_metadata_from_pdf
from fastapi.responses import JSONResponse
from scripts.extractor_ai import check_openai_available
router = APIRouter()


def get_db():
    """Provide a scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/publications/", response_model=List[schemas.PublicationOut])
async def list_publications(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Return a list of publications with optional pagination."""
    pubs = crud.get_publications(db, skip=skip, limit=limit)
    return [
        schemas.PublicationOut(
            **{k: v for k, v in pub.__dict__.items() if k != "tags"},
            tags=pub.tags_list
        )
        for pub in pubs
    ]


@router.post("/publications/bulk/arxiv/")
async def bulk_add_from_arxiv(limit: int = 100, category: str = "cs.AI"):
    """Starts background loading of arXiv publications by category and limit."""
    if not check_openai_available():
        return JSONResponse(
            status_code=503,
            content={"error": "AI service unavailable. Please check your OpenAI connection."}
        )

    Thread(target=background_arxiv_loader, args=(limit, category), daemon=True).start()
    return {"status": "started", "message": f"Started loading {limit} papers from arXiv [{category}]."}



@router.get("/publications/updated-since")
async def publications_updated_since(after: str = Query(...), db: Session = Depends(get_db)):
    """Check if new publications have been added since the given ISO timestamp."""
    try:
        after_dt = datetime.fromisoformat(after)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid timestamp format"})

    count = db.query(models.Publication).filter(models.Publication.created_at > after_dt).count()
    return {"updated": count > 0, "new_count": count}


def background_arxiv_loader(limit: int, category: str):
    """Load publications from arXiv in the background and store new ones in the database."""
    db = SessionLocal()
    collected = 0
    page_size = 25
    start = 0
    max_attempts = 10

    while collected < limit and max_attempts > 0:
        papers = fetch_arxiv_papers(limit=page_size, category=category, start=start)
        if not papers:
            print("❌ No more papers returned from arXiv.")
            break

        added_this_batch = 0

        for paper in papers:
            if crud.get_publication_by_pdf(db, paper["pdf_link"]):
                continue

            try:
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
                    val = combined.get(field)
                    if isinstance(val, list):
                        combined[field] = ", ".join(val)
                    elif val is None:
                        combined[field] = ""

                crud.create_publication(db, schemas.PublicationCreate(**combined))
                collected += 1
                added_this_batch += 1

                if collected >= limit:
                    break

            except Exception as e:
                print(f"❌ Error for {paper['pdf_link']}: {e}")
                continue

        start += page_size
        max_attempts -= 1

    db.close()


