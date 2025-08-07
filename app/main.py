import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import models
from app.database import engine, SessionLocal
from app.models import Publication
from app.views import router as publications_router
from scripts.downloader_arxiv import fetch_arxiv_categories

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(publications_router)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def show_publications(request: Request, page: int = 1, per_page: int = 2):
    """Render the main page with paginated list of publications."""
    skip = (page - 1) * per_page

    with SessionLocal() as db:
        total = db.query(Publication).count()
        total_pages = (total + per_page - 1) // per_page

        pubs = db.query(Publication).order_by(Publication.created_at.desc()).offset(skip).limit(per_page).all()

        for p in pubs:
            p.tags = json.loads(p.tags or "[]")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "publications": pubs,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total_publications": total,
        "categories": fetch_arxiv_categories()
    })
