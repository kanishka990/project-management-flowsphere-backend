from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException
from app.repositories.submenu_repository import SubMenuRepository
from app.schemas.submenu_schema import SubMenuCreate, SubMenuUpdate

class SubMenuService:
    def __init__(self, db: AsyncSession, submenu_repo: SubMenuRepository):
        self.db = db
        self.submenu_repo = submenu_repo

    async def create_submenu(self, payload: SubMenuCreate):
        return await self.submenu_repo.create(payload)

    async def get_submenu_by_id(self, submenu_id: UUID):
        submenu = await self.submenu_repo.get_by_id(submenu_id)
        if not submenu:
            raise ResourceNotFoundException("SubMenu")
        return submenu

    async def list_submenus(self, menu_id: UUID | None = None):
        return await self.submenu_repo.list(menu_id=menu_id)

    async def update_submenu(self, submenu_id: UUID, payload: SubMenuUpdate):
        submenu = await self.get_submenu_by_id(submenu_id)
        return await self.submenu_repo.update(
            submenu,
            title=payload.title,
            menu_id=payload.menu_id
        )

    async def delete_submenu(self, submenu_id: UUID):
        submenu = await self.get_submenu_by_id(submenu_id)
        await self.submenu_repo.delete(submenu)