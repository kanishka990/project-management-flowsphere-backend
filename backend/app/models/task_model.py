from __future__ import annotations

import uuid
from uuid import UUID as UUIDType
from typing import List, Optional

from sqlalchemy import String, Text, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

from app.models.subtask_model import SubTask

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.models.task_model import Task
    from app.models.task_assignment_model import TaskAssignment
    from app.models.timesheet_model import Timesheet
    from app.models.user_model import User

class Task(Base, FullAuditMixin):
    __tablename__ = "tasks"

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

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_hours: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
        lazy="selectin",
    )

    assignments: Mapped[List["TaskAssignment"]] = relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    timesheets: Mapped[List["Timesheet"]] = relationship(
        "Timesheet",
        back_populates="task",
        lazy="selectin",
    )

    subtasks: Mapped[List["SubTask"]] = relationship(
    "SubTask",
    back_populates="task",
    cascade="all, delete-orphan",
    lazy="selectin",
    )

    def __repr__(self):
        return f"<Task {self.title}>"