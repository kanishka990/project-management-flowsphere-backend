from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.menu_model import Menu
    from app.models.permission_model import Permission

class SubMenu(Base, FullAuditMixin):
    __tablename__ = "submenus"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    
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
