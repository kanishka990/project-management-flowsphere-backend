from __future__ import annotations

from typing import TYPE_CHECKING 
from uuid import UUID as UUIDType
import uuid

from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin
if TYPE_CHECKING:
    from app.models.user_model import User

class Department(Base, FullAuditMixin):
    __tablename__ = "departments"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="department",
        passive_deletes=True,
    )