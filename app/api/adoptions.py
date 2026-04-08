from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from datetime import datetime
from models import db_helper, Adoption, AdoptionStatus, Animal, AnimalStatus

router = APIRouter(tags=["Adoptions"], prefix="/applications")

# Pydantic схемы
class AdoptionCreate(BaseModel):
    animal_id: int
    message: Optional[str] = None

class AdoptionRead(BaseModel):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    user_name: Optional[str] = None
    message: Optional[str] = None
    status: AdoptionStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AdoptionUpdateStatus(BaseModel):
    comment: Optional[str] = None

# GET /applications - список заявок (с фильтрацией по ролям)
@router.get("", response_model=list[AdoptionRead])
async def get_applications(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    status: Optional[AdoptionStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    stmt = select(Adoption)
    if status:
        stmt = stmt.where(Adoption.status == status)
    if user_id:
        stmt = stmt.where(Adoption.user_id == user_id)
    stmt = stmt.offset(skip).limit(limit)
    
    result = await session.execute(stmt)
    return result.scalars().all()

# GET /applications/{id} - получить заявку по ID
@router.get("/{adoption_id}", response_model=AdoptionRead)
async def get_application(
    adoption_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    adoption = await session.get(Adoption, adoption_id)
    if not adoption:
        raise HTTPException(status_code=404, detail="Application not found")
    return adoption

# POST /applications - создать заявку
@router.post("", response_model=AdoptionRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    adoption_data: AdoptionCreate,
    # TODO: получить user_id из JWT токена (пока заглушка)
    user_id: int = 1  # временно
):
    # Проверка существования животного
    animal = await session.get(Animal, adoption_data.animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Проверка статуса животного
    if animal.status != AnimalStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Animal is not available")
    
    # Создание заявки
    adoption = Adoption(
        user_id=user_id,
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