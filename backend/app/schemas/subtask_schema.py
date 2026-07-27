from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.pagination import PaginationResponse


class SubTaskBase(BaseModel):
    task_id: UUID
    manager_id: UUID
    employee_id: UUID

    title: str
    description: Optional[str] = None

    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = 0

    priority: str = "Medium"
    status: str = "Pending"

    start_date: Optional[date] = None
    due_date: Optional[date] = None

    remarks: Optional[str] = None


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    priority: Optional[str] = None
    status: Optional[str] = None

    start_date: Optional[date] = None
    due_date: Optional[date] = None

    remarks: Optional[str] = None


class ManagerInfo(BaseModel):
    id: UUID
    emp_id: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class EmployeeInfo(BaseModel):
    id: UUID
    emp_id: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class SubTaskResponse(SubTaskBase):
    id: UUID

    created_at: datetime
    updated_at: datetime

    manager: Optional[ManagerInfo] = None
    employee: Optional[EmployeeInfo] = None

    model_config = ConfigDict(from_attributes=True)


class SubTaskListResponse(PaginationResponse):
    items: List[SubTaskResponse]