from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import date
from models import db_helper, Animal, AnimalStatus, AnimalType

router = APIRouter(tags=["Animals"], prefix="/animals")

# Pydantic схемы
class AnimalBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: AnimalType
    age: Optional[str] = Field(None, max_length=20)
    size: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    status: AnimalStatus = AnimalStatus.AVAILABLE

class AnimalCreate(AnimalBase):
    shelter_id: int

class AnimalUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[AnimalType] = None
    age: Optional[str] = Field(None, max_length=20)
    size: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[AnimalStatus] = None

class AnimalRead(AnimalBase):
    id: int
    shelter_id: int
    created_at: date
    
    class Config:
        from_attributes = True

# CRUD эндпоинты — ИСПРАВЛЕННЫЙ с фильтрацией по age и size
@router.get("", response_model=list[AnimalRead])
async def get_animals(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    type: Optional[AnimalType] = Query(None, description="Filter by type (dog/cat)"),
    age: Optional[str] = Query(None, description="Filter by age (baby/young/adult/senior)"),
    size: Optional[str] = Query(None, description="Filter by size (small/medium/large)"),
    status: Optional[AnimalStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    stmt = select(Animal)
    
    if type:
        stmt = stmt.where(Animal.type == type)
    if age:
        stmt = stmt.where(Animal.age == age)
    if size:
        stmt = stmt.where(Animal.size == size)
    if status:
        stmt = stmt.where(Animal.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await session.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
async def create_animal(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    animal_data: AnimalCreate
):
    animal = Animal(**animal_data.model_dump())
    session.add(animal)
    await session.commit()
    await session.refresh(animal)
    return animal

@router.get("/{animal_id}", response_model=AnimalRead)
async def get_animal(
    animal_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    animal = await session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal

@router.put("/{animal_id}", response_model=AnimalRead)
async def update_animal(
    animal_id: int,
    animal_update: AnimalUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    animal = await session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    update_data = animal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(animal, key, value)
    
    await session.commit()
    await session.refresh(animal)
    return animal

@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    animal = await session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    await session.delete(animal)
    await session.commit()