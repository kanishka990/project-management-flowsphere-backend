from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TimesheetBase(BaseModel):
    project_id: UUID
    task_id: UUID
    subtask: Optional[str] = None
    work_date: date
    hours: float = Field(..., gt=0, le=12)
    remarks: Optional[str] = None


class TimesheetCreate(TimesheetBase):

    @field_validator("work_date")
    @classmethod
    def validate_work_date(cls, value: date):
        if value > date.today():
            raise ValueError("Future dates are not allowed.")
        return value


class TimesheetUpdate(BaseModel):
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    subtask: Optional[str] = None
    work_date: Optional[date] = None
    hours: Optional[float] = Field(None, gt=0, le=12)
    remarks: Optional[str] = None

    @field_validator("work_date")
    @classmethod
    def validate_work_date(cls, value: Optional[date]):
        if value and value > date.today():
            raise ValueError("Future dates are not allowed.")
        return value


class TimesheetApprove(BaseModel):
    remarks: Optional[str] = None


class TimesheetReject(BaseModel):
    rejection_reason: str = Field(..., min_length=5)


class TimesheetResponse(TimesheetBase):
    id: UUID
    employee_id: UUID
    status: str
    approved_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from typing import List

from app.utils.pagination import PaginationResponse


class TimesheetListResponse(PaginationResponse):
    items: List[TimesheetResponse]