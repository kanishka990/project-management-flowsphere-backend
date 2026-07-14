from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class MenuBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    path: str | None = Field(None, max_length=255)
    icon: str | None = Field(None, max_length=100)
    sort_order: int = 0
    is_active: bool = True

class MenuCreate(MenuBase):
    code: str | None = Field(None, min_length=2, max_length=100)

class MenuUpdate(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    path: str | None = Field(None, max_length=255)
    icon: str | None = Field(None, max_length=100)
    sort_order: int | None = None
    is_active: bool | None = None

class MenuResponse(BaseModel):
    id: UUID
    code: str
    label: str
    path: str | None = None
    icon: str | None = None
    sort_order: int
    is_active: bool


    model_config = ConfigDict(from_attributes=True)

class NavigationChildResponse(BaseModel):
    id: UUID
    code: str
    label: str
    path: str | None = None
    icon: str | None = None

class NavigationMenuResponse(BaseModel):
    id: UUID
    code: str
    label: str
    path: str | None = None
    icon: str | None = None
    children: list[NavigationChildResponse] = Field(default_factory=list)

class NavigationResponse(BaseModel):
    menus: list[NavigationMenuResponse]
