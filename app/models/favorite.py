from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .animal import Animal

class Favorite(Base):
    __tablename__ = "favorites"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="favorites")
    animal: Mapped["Animal"] = relationship(back_populates="favorited_by")