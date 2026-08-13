from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID as UUIDType
import uuid

from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin
from app.models.associations_model import role_permissions

if TYPE_CHECKING:
    from app.models.role_model import Role
    from app.models.submenu_model import SubMenu

class Permission(Base, FullAuditMixin):
    __tablename__ = "permissions"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), unique=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    submenu_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submenus.id", ondelete="SET NULL"),
        nullable=True,
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="raise",
    )
    
    submenu: Mapped[Optional["SubMenu"]] = relationship(
        "SubMenu", 
        back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code='{self.code}')>"