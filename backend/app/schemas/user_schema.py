from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from app.schemas import role_schema

from app.schemas.role_schema import RoleResponse
from app.schemas.permission_schema import PermissionResponse

import re
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

# 1. The Base Schema (Shared properties)
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=15)
    department_id: UUID
    reporting_manager_id: Optional[UUID] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", v)
        if not re.match(r"^\+?\d{10,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

# 2. The Create Schema (Used when registering a new user)
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be 8-128 characters",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserSelfRegister(UserCreate):
    pass

class EmailVerificationResponse(BaseModel):
    detail: str
    token: Optional[str] = None # For dev purposes only

# 3. The Update Schema (Used for editing profiles)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    department_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None

from pydantic import computed_field

# 4. The Response Schema (Used when returning data to the frontend)
class UserResponse(BaseModel):           
    id: UUID
    email: EmailStr
    full_name: str
    phone_number: str
    department_id: UUID
    reporting_manager_id: Optional[UUID] = None
    
    emp_id: str         
    is_active: bool
    is_first_login: bool
    
    # Audit fields
    created_at: datetime
    updated_at: datetime

    # Composition: This is the correct way to attach roles and permission!
    roles: list[role_schema.RoleResponse] = []
    
    @computed_field
    @property
    def permissions(self) -> list[PermissionResponse]:
        """
        Dynamically calculates the flattened, unique list of permissions 
        assigned to this user through their roles during serialization.
        """
        unique_perms = {}
        for role in self.roles:
            for perm in role.permissions:
                unique_perms[perm.id] = perm
        return list(unique_perms.values())
    
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

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

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

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

