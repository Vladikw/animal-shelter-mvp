from fastapi import APIRouter
from config import settings
from .animals import router as animals_router
from .photos import router as photos_router

router = APIRouter(prefix=settings.url.prefix)
router.include_router(animals_router)
router.include_router(photos_router)