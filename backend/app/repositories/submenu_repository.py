from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.submenu_model import SubMenu
from app.schemas.submenu_schema import SubMenuCreate
from app.repositories.base_repository import BaseRepository

class SubMenuRepository(BaseRepository):
    
    async def get_by_id(self, submenu_id: UUID) -> SubMenu | None:
        stmt = select(SubMenu).where(SubMenu.id == submenu_id, SubMenu.is_deleted == False).options(
            selectinload(SubMenu.menu),
            selectinload(SubMenu.permissions)
        )
        return await self.session.scalar(stmt)

    async def list(self, menu_id: UUID | None = None) -> list[SubMenu]:
        stmt = (
            select(SubMenu)
            .where(SubMenu.is_deleted == False)
            .options(selectinload(SubMenu.permissions))
        )

        if menu_id:
            stmt = stmt.where(SubMenu.menu_id == menu_id)

        stmt = stmt.order_by(SubMenu.sort_order.asc(), SubMenu.title.asc())

        result = await self.session.scalars(stmt)
        return list(result.unique().all())

    async def create(self, payload: SubMenuCreate) -> SubMenu:
        code = payload.code or await self._generate_next_code(SubMenu, "code", "SBM")

        submenu = SubMenu(
            code=code,
            title=payload.title,
            menu_id=payload.menu_id,
            path=payload.path,
            icon=payload.icon,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
        self.session.add(submenu)
        await self.session.flush()
        await self.session.refresh(submenu)
        return submenu

    _UPDATABLE_FIELDS = frozenset({
        "title",
        "menu_id",
        "path",
        "icon",
        "sort_order",
        "is_active",
        "updated_by",
    })

    async def update(self, submenu: SubMenu, **kwargs) -> SubMenu:
        for key, value in kwargs.items():
            if key in self._UPDATABLE_FIELDS:
                setattr(submenu, key, value)
        await self.session.flush()
        await self.session.refresh(submenu)
        return submenu

    async def delete(self, submenu: SubMenu, deleted_by: UUID | None = None) -> None:
        submenu.is_active = False
        await self.soft_delete(submenu, deleted_by)

