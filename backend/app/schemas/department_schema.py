from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=255)

class DepartmentCreate(DepartmentBase):
    code: str = Field(..., max_length=20)

class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    code: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=255)

class DepartmentResponse(DepartmentBase):
    id: UUID
    code: str
    
    model_config = ConfigDict(from_attributes=True)
    
class DepartmentListResponse(BaseModel):
    items: list[DepartmentResponse]
    page: int
    page_size: int
    total: int
    pages: int


