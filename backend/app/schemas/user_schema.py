from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from app.schemas import role_schema

from app.schemas.role_schema import RoleResponse
from app.schemas.permission_schema import PermissionResponse

# 1. The Base Schema (Shared properties)
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: str

# 2. The Create Schema (Used when registering a new user)
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be 8-128 characters",
    )

# 3. The Update Schema (Used for editing profiles)
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

# 4. The Response Schema (Used when returning data to the frontend)
class UserResponse(UserBase):           
    emp_id: str         
    is_active: bool
    is_verified: bool
    is_first_login: bool
    
    # Audit fields
    created_at: datetime
    updated_at: datetime

    # Composition: This is the correct way to attach roles and permission!
    roles: list[role_schema.RoleResponse] = []
    permissions: list[PermissionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# 5. The Login Response Schema (Used when returning tokens after login)
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    require_password_change: bool = False
    message: str | None = None

# 6. The Login Request Schema (Used when logging in)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 7. The Password Change Request Schema (Used when changing password)
class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

# 8. The Role Schema (Used to assign and change roles)
class UserRoleReplace(BaseModel):
    role_ids: list[UUID] = Field(..., min_items=1)

# 9. The User List Response Schema (Used for paginated user lists)
class UserListResponse(BaseModel):
    items: list[UserResponse]
    page: int
    page_size: int
    total: int
    pages: int

# 10. The Password Reset Request Schema (Used when requesting a password reset)
class PasswordResetRequest(BaseModel):
    email: EmailStr