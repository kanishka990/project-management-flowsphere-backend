from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.pagination import PaginationResponse


# ============================================================
# ENUMS
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
# BASE SCHEMA
# ============================================================

class TimesheetBase(BaseModel):
    project_id: UUID
    task_id: UUID

    shared_task_id: Optional[str] = None

    subtask_id: Optional[UUID] = None

    deliverable: Optional[str] = None

    work_date: date

    priority: Optional[Priority] = None

    planned_hours: float = Field(..., gt=0, le=24)

    actual_hours: float = Field(..., gt=0, le=24)

    due_date: Optional[date] = None

    actual_completion_date: Optional[date] = None

    result_output: Optional[str] = None

    evidence_link: Optional[str] = None

    blocker_type: Optional[str] = None

    blocker_reason: Optional[str] = None

    next_action: Optional[str] = None

    remarks: Optional[str] = None


# ============================================================
# CREATE
# ============================================================

class TimesheetCreate(TimesheetBase):

    @field_validator("work_date")
    @classmethod
    def validate_work_date(cls, value: date):
        if value > date.today():
            raise ValueError("Future work dates are not allowed.")
        return value


# ============================================================
# UPDATE
# ============================================================

class TimesheetUpdate(BaseModel):

    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None

    shared_task_id: Optional[str] = None

    subtask_id: Optional[UUID] = None

    deliverable: Optional[str] = None

    work_date: Optional[date] = None

    priority: Optional[Priority] = None

    planned_hours: Optional[float] = Field(None, gt=0, le=24)

    actual_hours: Optional[float] = Field(None, gt=0, le=24)

    due_date: Optional[date] = None

    actual_completion_date: Optional[date] = None

    result_output: Optional[str] = None

    evidence_link: Optional[str] = None

    blocker_type: Optional[str] = None

    blocker_reason: Optional[str] = None

    next_action: Optional[str] = None

    remarks: Optional[str] = None

    @field_validator("work_date")
    @classmethod
    def validate_work_date(cls, value: Optional[date]):
        if value and value > date.today():
            raise ValueError("Future work dates are not allowed.")
        return value


# ============================================================
# APPROVE
# ============================================================

class TimesheetApprove(BaseModel):

    manager_rating: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
    )

    verification: VerificationStatus = VerificationStatus.VERIFIED

    hit_or_miss: Optional[HitMiss] = None

    remarks: Optional[str] = None


# ============================================================
# REJECT
# ============================================================

class TimesheetReject(BaseModel):

    rejection_reason: str = Field(
        ...,
        min_length=5,
    )

    remarks: Optional[str] = None


# ============================================================
# RESPONSE
# ============================================================

class TimesheetResponse(TimesheetBase):

    id: UUID

    employee_id: UUID

    status: TimesheetStatus

    verification: VerificationStatus

    manager_rating: Optional[int] = None

    hit_or_miss: Optional[HitMiss] = None

    approved_by: Optional[UUID] = None

    rejection_reason: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# LIST RESPONSE
# ============================================================

class TimesheetListResponse(PaginationResponse):

    items: List[TimesheetResponse]


# ============================================================
# EMPLOYEE SUMMARY
# ============================================================

class EmployeeSummary(BaseModel):

    employee_id: UUID

    total_tasks: int

    planned_hours: float

    actual_hours: float

    completed_tasks: int

    pending_tasks: int

    rejected_tasks: int

    blocked_tasks: int

    average_rating: Optional[float] = None

    performance_score: Optional[float] = None


# ============================================================
# TEAM SUMMARY
# ============================================================

class TeamSummary(BaseModel):

    total_employees: int

    total_tasks: int

    planned_hours: float

    actual_hours: float

    completed_tasks: int

    pending_tasks: int

    rejected_tasks: int

    blocked_tasks: int

    average_rating: Optional[float] = None

    average_performance: Optional[float] = None

# ============================================================
# SEARCH & FILTER
# ============================================================

class TimesheetFilter(BaseModel):
    employee_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    subtask_id: Optional[UUID] = None

    status: Optional[TimesheetStatus] = None
    priority: Optional[Priority] = None
    verification: Optional[VerificationStatus] = None
    hit_or_miss: Optional[HitMiss] = None

    # Renamed from start_date/end_date to from_date/to_date so this
    # schema can be unpacked directly into
    # TimesheetService.search_timesheets(**filter.model_dump())
    # without a keyword-argument mismatch.
    from_date: Optional[date] = None
    to_date: Optional[date] = None

    search: Optional[str] = None


# ============================================================
# PAGINATION
# ============================================================

class TimesheetPagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================
# SORTING
# ============================================================

class TimesheetSort(BaseModel):
    sort_by: str = Field(default="work_date")
    order: str = Field(default="desc", pattern="^(asc|desc)$")


# ============================================================
# REPORT ITEM
# ============================================================

class TimesheetReportItem(BaseModel):
    id: UUID
    employee_id: UUID
    project_id: UUID
    task_id: UUID
    subtask_id: Optional[UUID] = None

    work_date: date

    planned_hours: float
    actual_hours: float

    status: TimesheetStatus
    verification: VerificationStatus

    priority: Optional[Priority] = None

    manager_rating: Optional[int] = None

    hit_or_miss: Optional[HitMiss] = None

    deliverable: Optional[str] = None

    result_output: Optional[str] = None

    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# REPORT RESPONSE
# ============================================================

class TimesheetReportResponse(PaginationResponse):
    items: List[TimesheetReportItem]


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

class DashboardSummary(BaseModel):
    total_timesheets: int

    pending: int
    approved: int
    rejected: int

    verified: int
    rework_required: int

    planned_hours: float
    actual_hours: float

    utilization: float

    hit_rate: float

    average_rating: Optional[float] = None

    performance_score: Optional[float] = None


# ============================================================
# DAILY REPORT
# ============================================================

class DailyReport(BaseModel):
    work_date: date
    planned_hours: float
    actual_hours: float
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int


# ============================================================
# WEEKLY REPORT
# ============================================================

class WeeklyReport(BaseModel):
    week: str
    planned_hours: float
    actual_hours: float
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int


# ============================================================
# MONTHLY REPORT
# ============================================================

class MonthlyReport(BaseModel):
    month: str
    planned_hours: float
    actual_hours: float
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int


# ============================================================
# YEARLY REPORT
# ============================================================

class YearlyReport(BaseModel):
    year: int
    planned_hours: float
    actual_hours: float
    completed_tasks: int
    pending_tasks: int
    rejected_tasks: int


# ============================================================
# CHART DATA
# ============================================================

class ChartPoint(BaseModel):
    label: str
    value: float


class ChartResponse(BaseModel):
    title: str
    data: List[ChartPoint]