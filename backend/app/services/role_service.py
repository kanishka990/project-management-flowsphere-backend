from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceConflictException, ResourceNotFoundException, ValidationException
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.schemas.role_schema import RoleCreate, RoleUpdate

class RoleService:
    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo

    async def create_role(self, payload: RoleCreate):
        if await self.role_repo.get_by_name(payload.name):
            raise ValidationException("Role name already exists")
        
        role = await self.role_repo.create(payload)
        return role

    async def get_role_by_id(self, role_id: UUID):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise ResourceNotFoundException("Role")
        return role

    async def list_roles(
        self,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.role_repo.list(
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    async def update_role(self, role_id: UUID, payload: RoleUpdate):
        role = await self.get_role_by_id(role_id)
        return await self.role_repo.update(
            role,
            name=payload.name,
            description=payload.description,
        )

    async def delete_role(self, role_id: UUID, allow_if_assigned: bool = False):
        role = await self.get_role_by_id(role_id)
        if not allow_if_assigned and await self.role_repo.user_count(role) > 0:
            raise ResourceConflictException("Cannot delete a role that is assigned to users")
        await self.role_repo.delete(role)

    async def assign_permission(self, role_id: UUID, permission_id: UUID):
        role = await self.get_role_by_id(role_id)
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ResourceNotFoundException("Permission")
        await self.role_repo.assign_permission(role, permission)
        return permission

    async def remove_permission(self, role_id: UUID, permission_id: UUID):
        role = await self.get_role_by_id(role_id)
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ResourceNotFoundException("Permission")
        await self.role_repo.remove_permission(role, permission)
        return permission

    async def replace_permissions(self, role_id: UUID, permission_ids: list[UUID]):
        role = await self.get_role_by_id(role_id)
        permissions = []
        for permission_id in permission_ids:
            permission = await self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise ResourceNotFoundException("Permission")
            permissions.append(permission)
        await self.role_repo.replace_permissions(role, permissions)
        return permissions

    async def get_permissions(self, role_id: UUID):
        role = await self.get_role_by_id(role_id)
        return await self.role_repo.get_permissions(role)

    async def get_users(self, role_id: UUID):
        role = await self.get_role_by_id(role_id)
        return await self.role_repo.get_users(role)
