from __future__ import annotations

from uuid import UUID as UUIDType
import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, UUID, ForeignKey, CheckConstraint, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base
from app.db.mixins import FullAuditMixin
from app.models.associations_model import user_roles

if TYPE_CHECKING:
    from app.models.role_model import Role
    from app.models.department_model import Department
    from app.models.task_assignment_model import TaskAssignment
    from app.models.timesheet_model import Timesheet


class User(Base, FullAuditMixin):
    __tablename__ = "users"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emp_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_first_login: Mapped[bool] = mapped_column(default=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    department_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reporting_manager_id: Mapped[UUIDType | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reporting_manager: Mapped[User | None] = relationship(
        "User",
        remote_side=[id],
        backref="subordinates",
    )
    
    # Enforce at the DB level that a user cannot be their own manager
    __table_args__ = (
        CheckConstraint("id != reporting_manager_id", name="check_not_own_manager"),
        CheckConstraint("phone_number ~ '^\\+?[0-9]{10,15}$'", name="check_valid_phone_format"),
    )

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="raise",
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="users",
    )
    task_assignments: Mapped[list["TaskAssignment"]] = relationship(
        "TaskAssignment",
        foreign_keys="TaskAssignment.employee_id",
        back_populates="employee",
        lazy="selectin",
    )

    timesheets: Mapped[list["Timesheet"]] = relationship(
        "Timesheet",
        foreign_keys="Timesheet.employee_id",
        back_populates="employee",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', emp_id='{self.emp_id}')>"
