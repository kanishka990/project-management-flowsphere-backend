from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import uuid
from uuid import UUID

from app.db.base import Base
from app.db.mixins import FullAuditMixin
from app.models.role_model import Role

from app.models.associations_model import user_roles


class User(Base, FullAuditMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    emp_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    middle_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_first_login: Mapped[bool] = mapped_column(default=True)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )