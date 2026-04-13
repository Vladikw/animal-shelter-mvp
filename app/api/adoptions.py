from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import datetime
from models import db_helper, Adoption, AdoptionStatus, Animal, AnimalStatus, User, UserRole

router = APIRouter(tags=["Adoptions"], prefix="/applications")

# Pydantic схемы
class AdoptionCreate(BaseModel):
    animal_id: int
    user_name: str = Field(..., min_length=1, max_length=200)
    user_phone: str = Field(..., min_length=1, max_length=20)
    user_email: str = Field(..., min_length=1, max_length=200)
    message: Optional[str] = None

class AdoptionRead(BaseModel):
    id: int
    animal_id: int
    user_id: int
    message: Optional[str] = None
    status: AdoptionStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# POST /applications - создать заявку
@router.post("", response_model=AdoptionRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    adoption_data: AdoptionCreate,
):
    # Проверка существования животного
    animal = await session.get(Animal, adoption_data.animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Проверка статуса животного
    if animal.status != AnimalStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Animal is not available")
    
    # Найти или создать пользователя по email
    stmt = select(User).where(User.email == adoption_data.user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Создаем нового пользователя
        user = User(
            name=adoption_data.user_name,
            email=adoption_data.user_email,
            phone=adoption_data.user_phone,
            password_hash="temporary_for_mvp",  # временно, для ПР-04
            role=UserRole.ADOPTER
        )
        session.add(user)
        await session.flush()  # чтобы получить user.id
    
    # Создание заявки
    adoption = Adoption(
        user_id=user.id,  # ← теперь правильный user_id!
        animal_id=adoption_data.animal_id,
        message=adoption_data.message,
        status=AdoptionStatus.PENDING
    )
    session.add(adoption)
    await session.commit()
    await session.refresh(adoption)
    return adoption



# POST /applications/{id}/approve - одобрить заявку
@router.post("/{adoption_id}/approve", response_model=AdoptionRead)
async def approve_application(
    adoption_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    adoption = await session.get(Adoption, adoption_id)
    if not adoption:
        raise HTTPException(status_code=404, detail="Application not found")
    
    adoption.status = AdoptionStatus.APPROVED
    adoption.updated_at = datetime.utcnow()
    
    # Обновляем статус животного
    animal = await session.get(Animal, adoption.animal_id)
    if animal:
        animal.status = AnimalStatus.RESERVED
    
    await session.commit()
    await session.refresh(adoption)
    return adoption

# POST /applications/{id}/reject - отклонить заявку
@router.post("/{adoption_id}/reject", response_model=AdoptionRead)
async def reject_application(
    adoption_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    adoption = await session.get(Adoption, adoption_id)
    if not adoption:
        raise HTTPException(status_code=404, detail="Application not found")
    
    adoption.status = AdoptionStatus.REJECTED
    adoption.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(adoption)
    return adoption

# DELETE /applications/{id} - отменить заявку (только pending)
@router.delete("/{adoption_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_application(
    adoption_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    adoption = await session.get(Adoption, adoption_id)
    if not adoption:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if adoption.status != AdoptionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending applications can be cancelled")
    
    await session.delete(adoption)
    await session.commit()