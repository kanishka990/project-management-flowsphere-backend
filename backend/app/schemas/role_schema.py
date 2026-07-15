from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from app.schemas.permission_schema import PermissionResponse

# --- ROLES ---
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: Optional[list[UUID]] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    permissions: list[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RoleListResponse(BaseModel):
    items: list[RoleResponse]
    page: int
    page_size: int
    total: int
    pages: int

# --- ASSIGNMENTS & REPLACEMENTS ---
class UserRoleAssign(BaseModel):
    """Schema for assigning a role to a user via API"""
    user_id: UUID
    role_id: UUID

class RolePermissionReplace(BaseModel):
    permission_ids: List[UUID] = Field(..., min_items=1, description="List of valid Permission UUIDs")


