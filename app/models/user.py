from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey
from datetime import datetime
from .base import Base
import enum

if TYPE_CHECKING:
    from .shelter import Shelter
    from .favorite import Favorite
    from .notification import Notification
    from .adoption import Adoption

class UserRole(str, enum.Enum):
    ADOPTER = "adopter"
    SHELTER_STAFF = "shelter_staff"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.ADOPTER)
    shelter_id: Mapped[int | None] = mapped_column(ForeignKey("shelters.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    shelter: Mapped["Shelter | None"] = relationship(back_populates="staff")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    adoptions: Mapped[list["Adoption"]] = relationship(back_populates="user")