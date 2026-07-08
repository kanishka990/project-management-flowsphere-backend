from __future__ import annotations

import uuid
from datetime import date
from uuid import UUID as UUIDType
from typing import Optional

from sqlalchemy import Date, Float, ForeignKey, String, Text, UUID
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


class Timesheet(Base, FullAuditMixin):
    __tablename__ = "timesheets"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    employee_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subtask: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    remarks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
        nullable=False,
    )

    approved_by: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    employee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[employee_id],
        back_populates="timesheets",
        lazy="selectin",
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="timesheets",
        lazy="selectin",
    )

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="timesheets",
        lazy="selectin",
    )

    approver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[approved_by],
        lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<Timesheet(employee={self.employee_id}, "
            f"date={self.work_date}, hours={self.hours})>"
        )