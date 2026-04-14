from fastapi import APIRouter
from config import settings
from .animals import router as animals_router
from .photos import router as photos_router
from .adoptions import router as adoptions_router  
from .shelter import router as shelter_router

router = APIRouter(prefix=settings.url.prefix)
router.include_router(animals_router)
router.include_router(photos_router)
router.include_router(adoptions_router)   
router.include_router(shelter_router)