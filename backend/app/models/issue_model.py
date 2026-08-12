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
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.models.user_model import User


class IssueType(str, Enum):
    EPIC = "Epic"
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"
    IMPROVEMENT = "Improvement"
    SPIKE = "Spike"
    SUB_TASK = "Sub Task"


class IssueStatus(str, Enum):
    BACKLOG = "Backlog"
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    CODE_REVIEW = "Code Review"
    TESTING = "Testing"
    UAT = "UAT"
    DONE = "Done"
    CLOSED = "Closed"


class IssuePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Issue(Base, FullAuditMixin):
    __tablename__ = "issues"

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

    assignee_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reporter_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    issue_key: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    issue_type: Mapped[IssueType] = mapped_column(
        SQLEnum(IssueType, name="issue_type"),
        nullable=False,
        default=IssueType.TASK,
    )

    priority: Mapped[IssuePriority] = mapped_column(
        SQLEnum(IssuePriority, name="issue_priority"),
        nullable=False,
        default=IssuePriority.MEDIUM,
    )

    status: Mapped[IssueStatus] = mapped_column(
        SQLEnum(IssueStatus, name="issue_status"),
        nullable=False,
        default=IssueStatus.BACKLOG,
    )

    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    story_points: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="issues",
        lazy="selectin",
    )

    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_issues",
        lazy="selectin",
    )

    reporter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reporter_id],
        back_populates="reported_issues",
        lazy="selectin",
    )

    @property
    def project_name(self) -> str | None:
        return self.project.name if self.project else None

    @property
    def assignee_name(self) -> str | None:
        return self.assignee.full_name if self.assignee else None

    @property
    def reporter_name(self) -> str | None:
        return self.reporter.full_name if self.reporter else None

    def __repr__(self):
        return f"<Issue {self.issue_key}>"