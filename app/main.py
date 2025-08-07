from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app import models
from app.database import engine, SessionLocal
from app.views import router as publications_router
from app.models import Publication
import json

app = FastAPI()

# Создание таблиц в БД при запуске
models.Base.metadata.create_all(bind=engine)

# Подключаем роуты API
app.include_router(publications_router)

# Подключаем шаблоны и статические файлы
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Главная страница с HTML
@app.get("/", response_class=HTMLResponse)
async def show_publications(request: Request, page: int = 1, per_page: int = 2):
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
    })
