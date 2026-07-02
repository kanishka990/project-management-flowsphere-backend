from __future__ import annotations

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.submenu_model import SubMenu

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from app.db.base import Base

class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    submenus: Mapped[list["SubMenu"]] = relationship(
        "SubMenu", 
        back_populates="menu", 
        cascade="all, delete-orphan"
    )