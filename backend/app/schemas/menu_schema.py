from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class MenuBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)

class MenuResponse(MenuBase):
    id: UUID
    code: str

    model_config = ConfigDict(from_attributes=True)