from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.menu_model import Menu
from app.models.submenu_model import SubMenu
from app.schemas.menu_schema import MenuCreate
from app.repositories.base_repository import BaseRepository

class MenuRepository(BaseRepository):
    
    async def get_by_id(self, menu_id: UUID) -> Menu | None:
        stmt = select(Menu).where(
            Menu.id == menu_id,
            Menu.is_deleted == False
        ).options(
            selectinload(Menu.submenus).selectinload(SubMenu.permissions)
        )
        return await self.session.scalar(stmt)

    async def list(self) -> list[Menu]:
        stmt = (
            select(Menu)
            .where(Menu.is_deleted == False)
            .options(
                selectinload(Menu.submenus).selectinload(SubMenu.permissions)
            )
            .order_by(Menu.sort_order.asc(), Menu.name.asc())
        )
        result = await self.session.scalars(stmt)
        return list(result.unique().all())

    async def create(self, payload: MenuCreate) -> Menu:
        code = payload.code or await self._generate_next_code(Menu, "code", "MNU")

        menu = Menu(
            code=code,
            name=payload.name,
            path=payload.path,
            icon=payload.icon,
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
        self.session.add(menu)
        await self.session.flush()
        await self.session.refresh(menu)
        return menu

    _UPDATABLE_FIELDS = frozenset({
        "name",
        "path",
        "icon",
        "sort_order",
        "is_active",
        "updated_by",
    })

    async def update(self, menu: Menu, **kwargs) -> Menu:
        for key, value in kwargs.items():
            if key in self._UPDATABLE_FIELDS:
                setattr(menu, key, value)
        await self.session.flush()
        await self.session.refresh(menu)
        return menu

    async def delete(self, menu: Menu, deleted_by: UUID | None = None) -> None:
        menu.is_active = False
        await self.soft_delete(menu, deleted_by)
