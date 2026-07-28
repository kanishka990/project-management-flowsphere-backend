from __future__ import annotations

import uuid
from uuid import UUID as UUIDType
from typing import Optional

from sqlalchemy import ForeignKey, String, UUID
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


class TaskAssignment(Base, FullAuditMixin):
    __tablename__ = "task_assignments"

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

    employee_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_by: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Assigned",
        nullable=False,
    )

    remarks: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="assignments",
        lazy="selectin",
    )

    employee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[employee_id],
        back_populates="task_assignments",
        lazy="selectin",
    )

    assigned_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_by],
        lazy="selectin",
    )

    @property
    def employee_name(self) -> str | None:
        return self.employee.full_name if self.employee else None


    @property
    def assigned_by_name(self) -> str | None:
        return (
            self.assigned_user.full_name
            if self.assigned_user
            else None
        )

    def __repr__(self):
        return f"<TaskAssignment {self.id}>"