from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from models import db_helper, Photo, Animal

router = APIRouter(tags=["Photos"], prefix="/photos")

class PhotoRead(BaseModel):
    id: int
    animal_id: int
    url: str
    
    class Config:
        from_attributes = True

@router.get("/animal/{animal_id}", response_model=list[PhotoRead])
async def get_animal_photos(
    animal_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    result = await session.execute(
        select(Photo).where(Photo.animal_id == animal_id)
    )
    return result.scalars().all()