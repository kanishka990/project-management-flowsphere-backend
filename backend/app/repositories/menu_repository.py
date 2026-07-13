from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.menu_model import Menu
from app.schemas.menu_schema import MenuCreate
from app.repositories.base_repository import BaseRepository

class MenuRepository(BaseRepository):
    
    async def get_by_id(self, menu_id: UUID) -> Menu | None:
        stmt = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False).options(
            selectinload(Menu.submenus)
        )
        return await self.session.scalar(stmt)

    async def list(self) -> list[Menu]:
        stmt = select(Menu).where(Menu.is_deleted == False).options(
            selectinload(Menu.submenus)
        ).order_by(Menu.code.asc())
        
        result = await self.session.scalars(stmt)
        return list(result.unique().all())

    async def create(self, payload: MenuCreate) -> Menu:
        new_code = await self._generate_next_code(Menu, "code", "MNU")
        
        menu = Menu(
            code=new_code, 
            name=payload.name
        )
        self.session.add(menu)
        await self.session.flush()
        await self.session.refresh(menu)
        return menu

    _UPDATABLE_FIELDS = frozenset({"name", "updated_by"})

    async def update(self, menu: Menu, **kwargs) -> Menu:
        for key, value in kwargs.items():
            if key in self._UPDATABLE_FIELDS:
                setattr(menu, key, value)
        await self.session.flush()
        await self.session.refresh(menu)
        return menu

    async def delete(self, menu: Menu) -> None:
        await self.session.delete(menu)
        await self.session.flush()
