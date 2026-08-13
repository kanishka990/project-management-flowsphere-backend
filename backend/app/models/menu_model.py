from __future__ import annotations

from typing import TYPE_CHECKING 
from uuid import UUID as UUIDType
import uuid

if TYPE_CHECKING:
    from app.models.submenu_model import SubMenu

from sqlalchemy import Boolean, Integer, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

class Menu(Base, FullAuditMixin):
    __tablename__ = "menus"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    submenus: Mapped[list["SubMenu"]] = relationship(
        "SubMenu", 
        back_populates="menu", 
        cascade="all, delete-orphan"
    )
