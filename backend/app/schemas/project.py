from __future__ import annotations

from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    status: str = "Active"
    manager_id: UUID


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    manager_id: Optional[UUID] = None


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from typing import List

from app.utils.pagination import PaginationResponse


class ProjectListResponse(PaginationResponse):
    items: List[ProjectResponse]