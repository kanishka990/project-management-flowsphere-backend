from __future__ import annotations
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.user_model import User
from app.models.associations_model import user_roles
from app.schemas.role_schema import RoleCreate
from app.utils.pagination import paginate

from app.repositories.base_repository import BaseRepository

class RoleRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, role_id: UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id, Role.is_deleted == False).options(
            selectinload(Role.permissions),
            selectinload(Role.users),
            selectinload(Role.users).selectinload(User.roles).selectinload(Role.permissions),
            selectinload(Role.users).selectinload(User.reporting_manager),
            selectinload(Role.users).selectinload(User.department),
        )
        return await self.session.scalar(stmt)

    async def get_with_permissions(self, role_id: UUID) -> Role | None:
        stmt = (
            select(Role)
            .where(Role.id == role_id, Role.is_deleted == False)
            .options(selectinload(Role.permissions))
        )
        return await self.session.scalar(stmt)

    async def get_by_ids(self, role_ids: list[UUID]) -> list[Role]:
        if not role_ids:
            return []

        stmt = select(Role).where(
            Role.id.in_(role_ids),
            Role.is_deleted == False,
        ).options(selectinload(Role.permissions))
        result = await self.session.scalars(stmt)
        return result.unique().all()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = (
            select(Role)
            .where(func.lower(Role.name) == name.lower(), Role.is_deleted == False)
            .options(
                selectinload(Role.permissions),
                selectinload(Role.users),
                selectinload(Role.users).selectinload(User.roles).selectinload(Role.permissions),
                selectinload(Role.users).selectinload(User.reporting_manager),
                selectinload(Role.users).selectinload(User.department),
            )
        )
        return await self.session.scalar(stmt)

    async def list(
        self,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Role], int, int]:
        stmt = select(Role).where(Role.is_deleted == False).options(selectinload(Role.permissions))
        if search:
            query = f"%{search.strip().lower()}%"
            stmt = stmt.where(func.lower(Role.name).like(query))
        stmt = self._apply_sorting(stmt, Role, sort_by, sort_order)
        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def create(
        self,
        payload: RoleCreate,
        permissions: list[Permission] | None = None,
    ) -> Role:
        role = Role(
            name=payload.name,
            description=payload.description,
            permissions=permissions or [],
        )
        self.session.add(role)
        await self.session.flush()
        loaded_role = await self.get_with_permissions(role.id)
        return loaded_role or role

    _UPDATABLE_FIELDS = frozenset({"name", "description", "updated_by"})

    async def update(self, role: Role, **kwargs) -> Role:
        for key, value in kwargs.items():
            if key in self._UPDATABLE_FIELDS:
                setattr(role, key, value)
        await self.session.flush()
        loaded_role = await self.get_with_permissions(role.id)
        return loaded_role or role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
        await self.session.flush()

    async def assign_permission(self, role: Role, permission: Permission) -> None:
        if permission not in role.permissions:
            role.permissions.append(permission)
            await self.session.flush()

    async def remove_permission(self, role: Role, permission: Permission) -> None:
        if permission in role.permissions:
            role.permissions.remove(permission)
            await self.session.flush()

    async def replace_permissions(self, role: Role, permissions: list[Permission]) -> None:
        role.permissions = permissions
        await self.session.flush()

    async def get_permissions(self, role: Role) -> list[Permission]:
        return role.permissions

    async def get_users(self, role: Role) -> list[User]:
        return role.users

    async def user_count(self, role: Role) -> int:
        stmt = select(func.count()).select_from(user_roles).where(user_roles.c.role_id == role.id)
        return await self.session.scalar(stmt)

