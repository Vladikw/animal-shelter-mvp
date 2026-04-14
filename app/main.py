import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from config import settings
from contextlib import asynccontextmanager

from models import db_helper, Base
from api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await db_helper.dispose()

main_app = FastAPI(lifespan=lifespan)

# Подключаем API роутеры
main_app.include_router(api_router)

# Статические файлы (CSS, JS)
main_app.mount("/static", StaticFiles(directory="static"), name="static")

# === ПРОСТЫЕ HTML СТРАНИЦЫ (без Jinja2) ===

@main_app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@main_app.get("/animals", response_class=HTMLResponse)
async def animals_page():
    with open("templates/animals.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@main_app.get("/application", response_class=HTMLResponse)
async def application_page():
    with open("templates/application.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    
@main_app.get("/favorites", response_class=HTMLResponse)
async def favorites_page():
    with open("templates/favorites.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@main_app.get("/animal/{animal_id}", response_class=HTMLResponse)
async def animal_card_page(animal_id: int):
    with open("templates/animal_card.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@main_app.get("/shelter-panel", response_class=HTMLResponse)
async def shelter_panel():
    with open("templates/shelter_panel.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )