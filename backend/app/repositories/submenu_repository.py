from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.submenu_model import SubMenu
from app.schemas.submenu_schema import SubMenuCreate
from app.repositories.base_repository import BaseRepository

class SubMenuRepository(BaseRepository):
    
    async def get_by_id(self, submenu_id: UUID) -> SubMenu | None:
        stmt = select(SubMenu).where(SubMenu.id == submenu_id).options(
            selectinload(SubMenu.menu),
            selectinload(SubMenu.permissions)
        )
        return await self.session.scalar(stmt)

    async def list(self, menu_id: UUID | None = None) -> list[SubMenu]:
        stmt = select(SubMenu).options(
            selectinload(SubMenu.permissions)
        )
        
        if menu_id:
            stmt = stmt.where(SubMenu.menu_id == menu_id)
            
        stmt = stmt.order_by(SubMenu.code.asc())
        result = await self.session.scalars(stmt)
        return list(result.unique().all())

    async def create(self, payload: SubMenuCreate) -> SubMenu:
        new_code = await self._generate_next_code(SubMenu, "SBM")
        
        submenu = SubMenu(
            code=new_code,
            title=payload.title,
            menu_id=payload.menu_id
        )
        self.session.add(submenu)
        await self.session.flush()
        await self.session.refresh(submenu)
        return submenu

    async def update(self, submenu: SubMenu, **kwargs) -> SubMenu:
        for key, value in kwargs.items():
            if hasattr(submenu, key) and value is not None:
                setattr(submenu, key, value)
        await self.session.flush()
        await self.session.refresh(submenu)
        return submenu

    async def delete(self, submenu: SubMenu) -> None:
        await self.session.delete(submenu)
        await self.session.flush()