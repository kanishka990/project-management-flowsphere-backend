from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from uuid import UUID as UUIDType

from sqlalchemy import UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.models.user_model import User


class ProjectMember(Base, FullAuditMixin):
    __tablename__ = "project_members"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member",
        ),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="project_members",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="project_members",
    )