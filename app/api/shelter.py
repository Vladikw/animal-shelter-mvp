from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime 
from models import db_helper, Adoption, AdoptionStatus, Animal, AnimalStatus, Shelter, User
from .animals import AnimalRead

router = APIRouter(tags=["Shelter"], prefix="/shelter")

# Схема для ответа с заявкой (включая данные о животном и заявителе)
class AdoptionWithDetails(BaseModel):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    user_name: str
    user_phone: str
    user_email: str
    message: Optional[str] = None
    status: AdoptionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/{shelter_id}/applications", response_model=list[AdoptionWithDetails])
async def get_shelter_applications(
    shelter_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    status_filter: Optional[AdoptionStatus] = None
):
    """
    Получить все заявки на животных конкретного приюта.
    Для MVP используем shelter_id=1 (первый приют)
    """
    # Сначала найдем всех животных этого приюта
    animals_stmt = select(Animal.id).where(Animal.shelter_id == shelter_id)
    animals_result = await session.execute(animals_stmt)
    animal_ids = [row[0] for row in animals_result.all()]
    
    if not animal_ids:
        return []
    
    # Находим заявки на этих животных
    stmt = select(Adoption).where(Adoption.animal_id.in_(animal_ids))
    if status_filter:
        stmt = stmt.where(Adoption.status == status_filter)
    
    result = await session.execute(stmt)
    adoptions = result.scalars().all()
    
    # Для каждой заявки подгружаем данные пользователя и животного
    result_list = []
    for adoption in adoptions:
        # Получаем пользователя
        user_stmt = select(User).where(User.id == adoption.user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        # Получаем животное
        animal_stmt = select(Animal).where(Animal.id == adoption.animal_id)
        animal_result = await session.execute(animal_stmt)
        animal = animal_result.scalar_one_or_none()
        
        if user:
            result_list.append(AdoptionWithDetails(
                id=adoption.id,
                animal_id=adoption.animal_id,
                animal_name=animal.name if animal else "Неизвестно",
                user_name=user.name,
                user_phone=user.phone,
                user_email=user.email,
                message=adoption.message,
                status=adoption.status,
                created_at=adoption.created_at
            ))
    
    return result_list

@router.get("/{shelter_id}/animals", response_model=list[AnimalRead])
async def get_shelter_animals(
    shelter_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    """Получить всех животных приюта для управления"""
    stmt = select(Animal).where(Animal.shelter_id == shelter_id)
    result = await session.execute(stmt)
    return result.scalars().all()