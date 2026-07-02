from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.user_model import User
from app.models.associations_model import user_roles
from app.schemas.role_schema import RoleCreate
from app.utils.pagination import paginate

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id).options(
            selectinload(Role.permissions),
            selectinload(Role.users),
        )
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(func.lower(Role.name) == name.lower())
        return await self.session.scalar(stmt)

    async def list(
        self,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Role], int, int]:
        stmt = select(Role).options(selectinload(Role.permissions))
        if search:
            query = f"%{search.strip().lower()}%"
            stmt = stmt.where(func.lower(Role.name).like(query))
        order_column = Role.created_at if sort_by == "created_at" else Role.updated_at
        stmt = stmt.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())
        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def create(self, payload: RoleCreate) -> Role:
        role = Role(
            name=payload.name,
            description=payload.description,
        )
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def update(self, role: Role, **kwargs) -> Role:
        for key, value in kwargs.items():
            if hasattr(role, key) and value is not None:
                setattr(role, key, value)
        await self.session.flush()
        await self.session.refresh(role)
        return role

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