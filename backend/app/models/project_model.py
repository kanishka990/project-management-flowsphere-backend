from __future__ import annotations

import uuid
from uuid import UUID as UUIDType
from typing import List, Optional

from sqlalchemy import String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.models.task_model import Task
    from app.models.task_assignment_model import TaskAssignment
    from app.models.timesheet_model import Timesheet
    from app.models.user_model import User


class Project(Base, FullAuditMixin):
    __tablename__ = "projects"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Active",
        nullable=False,
    )

    manager_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    timesheets: Mapped[List["Timesheet"]] = relationship(
        "Timesheet",
        back_populates="project",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Project {self.name}>"