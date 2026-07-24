from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.pagination import PaginationResponse


class TaskBase(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    priority: str = "Medium"
    status: str = "Pending"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TaskAssignmentInfo(BaseModel):
    employee_id: UUID
    employee_name: str
    assigned_by: UUID
    assigned_by_name: str
    status: str
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    assignment: Optional[TaskAssignmentInfo] = None

    model_config = ConfigDict(from_attributes=True)


class TaskAssignmentCreate(BaseModel):
    employee_id: UUID
    remarks: Optional[str] = None


class TaskAssignmentResponse(BaseModel):
    id: UUID
    task_id: UUID
    employee_id: UUID
    assigned_by: UUID
    status: str
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(PaginationResponse):
    items: List[TaskResponse]