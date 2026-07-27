from __future__ import annotations

import uuid
from uuid import UUID as UUIDType
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    UUID,
    String,
    Text,
    Float,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.task_model import Task
    from app.models.user_model import User
    from app.models.timesheet_model import Timesheet


class SubTask(Base, FullAuditMixin):
    __tablename__ = "subtasks"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    task_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    manager_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    employee_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_hours: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    actual_hours: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
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

    start_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
    )

    due_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
    )

    remarks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="subtasks",
        lazy="selectin",
    )

    manager: Mapped["User"] = relationship(
        "User",
        foreign_keys=[manager_id],
        lazy="selectin",
    )

    employee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[employee_id],
        lazy="selectin",
    )

    timesheets: Mapped[list["Timesheet"]] = relationship(
        "Timesheet",
        back_populates="subtask",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<SubTask("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"employee={self.employee_id}, "
            f"status='{self.status}')>"
        )