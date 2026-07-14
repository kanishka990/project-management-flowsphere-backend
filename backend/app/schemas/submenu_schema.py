from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class SubMenuBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    menu_id: UUID
    path: str | None = Field(None, max_length=255)
    icon: str | None = Field(None, max_length=100)
    sort_order: int = 0
    is_active: bool = True

class SubMenuCreate(SubMenuBase):
    code: str | None = Field(None, min_length=2, max_length=100)

class SubMenuUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    menu_id: UUID | None = None
    path: str | None = Field(None, max_length=255)
    icon: str | None = Field(None, max_length=100)
    sort_order: int | None = None
    is_active: bool | None = None

class SubMenuResponse(BaseModel):
    id: UUID
    code: str
    title: str
    menu_id: UUID
    path: str | None = None
    icon: str | None = None
    sort_order: int
    is_active: bool


    model_config = ConfigDict(from_attributes=True)
