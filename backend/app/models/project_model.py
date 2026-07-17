from __future__ import annotations

import uuid
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID as UUIDType

from sqlalchemy import (
    UUID,
    Date,
    Enum as SQLEnum,
    Float,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import FullAuditMixin

if TYPE_CHECKING:
    from app.models.project_member_model import ProjectMember
    from app.models.task_model import Task
    from app.models.timesheet_model import Timesheet


class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    UAT = "UAT"
    COMPLETED = "Completed"
    CLOSED = "Closed"


class ProjectPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


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

    start_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.DRAFT,
    )

    priority: Mapped[ProjectPriority] = mapped_column(
        SQLEnum(ProjectPriority, name="project_priority"),
        nullable=False,
        default=ProjectPriority.MEDIUM,
    )

    budget: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
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

    project_members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Project {self.name}>"