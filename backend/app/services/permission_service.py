from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceConflictException, ResourceNotFoundException, ValidationException
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.permission_schema import PermissionCreate, PermissionUpdate

class PermissionService:
    def __init__(
        self,
        db: AsyncSession,
        permission_repo: PermissionRepository,
        role_repo: RoleRepository,
    ):
        self.db = db
        self.permission_repo = permission_repo
        self.role_repo = role_repo

    async def create_permission(self, payload: PermissionCreate):
        return await self.permission_repo.create(payload)

    async def get_permission_by_id(self, permission_id: int):
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ResourceNotFoundException("Permission")
        return permission

    async def list_permissions(
        self,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.permission_repo.list(
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    async def update_permission(self, permission_id: int, payload: PermissionUpdate):
        permission = await self.get_permission_by_id(permission_id)
        return await self.permission_repo.update(
            permission,
            code=payload.code,
            description=payload.description,
        )

    async def delete_permission(self, permission_id: int, allow_if_assigned: bool = False):
        permission = await self.get_permission_by_id(permission_id)
        if not allow_if_assigned and permission.roles:
            raise ResourceConflictException("Cannot delete a permission that is assigned to roles")
        await self.permission_repo.delete(permission)

    async def get_roles(self, permission_id: int):
        permission = await self.get_permission_by_id(permission_id)
        return await self.permission_repo.get_roles(permission)

    async def get_users(self, permission_id: int):
        return await self.permission_repo.get_users(permission_id)