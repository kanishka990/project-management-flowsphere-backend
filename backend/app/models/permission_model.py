from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from uuid import UUID

from app.db.base import Base
from app.db.mixins import FullAuditMixin
from app.models.associations_model import role_permissions

if TYPE_CHECKING:
    from app.models.role_model import Role
    from app.models.submenu_model import SubMenu

class Permission(Base, FullAuditMixin):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    submenu_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("submenus.id", ondelete="SET NULL"), nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )
    
    submenu: Mapped[Optional["SubMenu"]] = relationship(
        "SubMenu", 
        back_populates="permissions"
    )