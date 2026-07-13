from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_schema import MenuCreate, MenuUpdate

class MenuService:
    def __init__(self, menu_repo: MenuRepository):
        self.menu_repo = menu_repo

    async def create_menu(self, payload: MenuCreate):
        return await self.menu_repo.create(payload)

    async def get_menu_by_id(self, menu_id: UUID):
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise ResourceNotFoundException("Menu")
        return menu

    async def list_menus(self):
        return await self.menu_repo.list()

    async def update_menu(self, menu_id: UUID, payload: MenuUpdate):
        menu = await self.get_menu_by_id(menu_id)
        return await self.menu_repo.update(
            menu,
            name=payload.name
        )

    async def delete_menu(self, menu_id: UUID):
        menu = await self.get_menu_by_id(menu_id)
        await self.menu_repo.delete(menu)

