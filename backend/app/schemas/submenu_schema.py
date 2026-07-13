from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class SubMenuBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    menu_id: UUID

class SubMenuCreate(SubMenuBase):
    pass

class SubMenuUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    menu_id: UUID | None = None

class SubMenuResponse(BaseModel):
    id: UUID
    code: str
    title: str
    menu_id: UUID

    model_config = ConfigDict(from_attributes=True)
