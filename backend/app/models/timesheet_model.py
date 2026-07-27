from __future__ import annotations

import uuid
from datetime import date
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID as UUIDType

from sqlalchemy import (
    UUID,
    Date,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.models.task_model import Task
    from app.models.subtask_model import SubTask
    from app.models.user_model import User


# ============================================================
# Enums
# ============================================================

class TimesheetStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class VerificationStatus(str, Enum):
    PENDING = "Pending"
    VERIFIED = "Verified"
    REWORK_REQUIRED = "Rework Required"


class HitMiss(str, Enum):
    HIT = "Hit"
    MISS = "Miss"
    BLOCKED = "Blocked"


# ============================================================
# Model
# ============================================================

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

    # =====================================================
    # Work Details
    # =====================================================

    shared_task_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    subtask_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subtasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    deliverable: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    priority: Mapped[Optional[Priority]] = mapped_column(
        SQLEnum(Priority),
        nullable=True,
    )

    planned_hours: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    actual_hours: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    actual_completion_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # =====================================================
    # Status
    # =====================================================

    status: Mapped[TimesheetStatus] = mapped_column(
        SQLEnum(TimesheetStatus),
        default=TimesheetStatus.PENDING,
        nullable=False,
    )

    verification: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    hit_or_miss: Mapped[Optional[HitMiss]] = mapped_column(
        SQLEnum(HitMiss),
        nullable=True,
    )

    manager_rating: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )

    # =====================================================
    # Output
    # =====================================================

    result_output: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_link: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    blocker_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    blocker_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    next_action: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    remarks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Approval
    # =====================================================

    approved_by: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Relationships
    # =====================================================

    employee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[employee_id],
        back_populates="timesheets",
        lazy="selectin",
    )

    approver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[approved_by],
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

    subtask: Mapped["SubTask"] = relationship(
        "SubTask",
        back_populates="timesheets",
        lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<Timesheet("
            f"id={self.id}, "
            f"employee={self.employee_id}, "
            f"project={self.project_id}, "
            f"task={self.task_id}, "
            f"subtask={self.subtask_id}, "
            f"date={self.work_date}, "
            f"actual_hours={self.actual_hours}, "
            f"status={self.status.value})>"
        )