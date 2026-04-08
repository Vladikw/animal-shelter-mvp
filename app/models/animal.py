from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Date, Enum, ForeignKey, Text
from datetime import date
from .base import Base
import enum

if TYPE_CHECKING:
    from .shelter import Shelter
    from .photo import Photo
    from .favorite import Favorite
    from .adoption import Adoption

class AnimalType(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"

class AnimalStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    ADOPTED = "adopted"

class Animal(Base):
    __tablename__ = "animals"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    type: Mapped[AnimalType] = mapped_column(Enum(AnimalType))
    age: Mapped[str | None] = mapped_column(String(20))  # baby, young, adult, senior
    size: Mapped[str | None] = mapped_column(String(20))  # small, medium, large
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[AnimalStatus] = mapped_column(Enum(AnimalStatus), default=AnimalStatus.AVAILABLE)
    shelter_id: Mapped[int] = mapped_column(ForeignKey("shelters.id", ondelete="CASCADE"))
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Relationships
    shelter: Mapped["Shelter"] = relationship(back_populates="animals")
    photos: Mapped[list["Photo"]] = relationship(back_populates="animal", cascade="all, delete-orphan")
    favorited_by: Mapped[list["Favorite"]] = relationship(back_populates="animal", cascade="all, delete-orphan")
    adoptions: Mapped[list["Adoption"]] = relationship(back_populates="animal")