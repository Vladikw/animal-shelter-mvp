from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text
from datetime import datetime
from .base import Base
import enum

if TYPE_CHECKING:
    from .user import User
    from .animal import Animal

class AdoptionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Adoption(Base):
    __tablename__ = "adoptions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id", ondelete="CASCADE"))
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[AdoptionStatus] = mapped_column(Enum(AdoptionStatus), default=AdoptionStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="adoptions")
    animal: Mapped["Animal"] = relationship(back_populates="adoptions")