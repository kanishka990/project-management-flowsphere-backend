from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID # Add this import

class PermissionBase(BaseModel):
    description: Optional[str] = None
    submenu_id: Optional[UUID] = None
    action: str = Field(..., min_length=3, max_length=128)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    description: Optional[str] = None
    submenu_id: Optional[UUID] = None

class PermissionResponse(BaseModel):
    id: UUID
    code: str
    description: Optional[str] = None
    submenu_id: Optional[UUID] = None
    action: str

    model_config = ConfigDict(from_attributes=True)

class PermissionListResponse(BaseModel):
    items: list[PermissionResponse]
    page: int
    page_size: int
    total: int
    pages: int

