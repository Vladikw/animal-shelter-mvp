from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .animal import Animal

class Photo(Base):
    __tablename__ = "photos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    animal: Mapped["Animal"] = relationship(back_populates="photos")