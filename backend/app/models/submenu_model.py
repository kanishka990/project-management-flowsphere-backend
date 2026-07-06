from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID as UUIDType
import uuid

from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.menu_model import Menu
    from app.models.permission_model import Permission

class SubMenu(Base):
    __tablename__ = "submenus"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    
    menu_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menus.id", ondelete="CASCADE")
    )

    menu: Mapped["Menu"] = relationship(
        "Menu", 
        back_populates="submenus"
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", 
        back_populates="submenu",
        cascade="all, delete-orphan"
    )