from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .animal import Animal

class Shelter(Base):
    __tablename__ = "shelters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(500))
    phone: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    staff: Mapped[list["User"]] = relationship(back_populates="shelter")
    animals: Mapped[list["Animal"]] = relationship(back_populates="shelter")