from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.permission_model import Permission
from app.models.role_model import Role
from app.models.user_model import User
from app.models.associations_model import role_permissions, user_roles
from app.schemas.permission_schema import PermissionCreate
from app.utils.pagination import paginate

class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, permission_id: int) -> Permission | None:
        stmt = (
            select(Permission)
            .where(Permission.id == permission_id)
            .options(
                selectinload(Permission.roles),
                selectinload(Permission.submenu)
            )
        )
        return await self.session.scalar(stmt)

    async def get_by_code(self, code: str) -> Permission | None:
        stmt = select(Permission).where(func.lower(Permission.code) == code.lower())
        return await self.session.scalar(stmt)

    async def list(
        self,
        search: str | None = None,
        submenu_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Permission], int, int]:
        stmt = select(Permission).options(
            selectinload(Permission.roles),
            selectinload(Permission.submenu)
        )
        if search:
            query = f"%{search.strip().lower()}%"
            stmt = stmt.where(func.lower(Permission.code).like(query))
        if submenu_id:
            stmt = stmt.where(Permission.submenu_id == submenu_id)
        order_column = Permission.created_at if sort_by == "created_at" else Permission.updated_at
        stmt = stmt.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())
        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def _generate_next_code(self, prefix: str = "PRM") -> str:
        stmt = (
            select(Permission.code)
            .where(Permission.code.like(f"{prefix}%"))
            .order_by(Permission.code.desc())
            .limit(1)
        )
        last_code = await self.session.scalar(stmt)
        if last_code and last_code.startswith(prefix):
            next_number = int(last_code.replace(prefix, "")) + 1
        else:
            next_number = 1
        return f"{prefix}{next_number:06d}"

    async def create(self, payload: PermissionCreate) -> Permission:
        permission = Permission(
            code=await self._generate_next_code("PRM"),
            action=payload.action.lower(),
            description=payload.description,
            submenu_id=payload.submenu_id,
        )
        self.session.add(permission)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission

    async def update(self, permission: Permission, **kwargs) -> Permission:
        for key, value in kwargs.items():
            # Prevent overriding relationships directly via kwargs if needed
            if hasattr(permission, key) and value is not None:
                setattr(permission, key, value)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission

    async def delete(self, permission: Permission) -> None:
        await self.session.delete(permission)
        await self.session.flush()

    async def get_roles(self, permission: Permission) -> list[Role]:
        return permission.roles

    async def get_users(self, permission_id: int) -> list[User]:
        stmt = (
            select(User)
            .join(user_roles, User.id == user_roles.c.user_id)
            .join(Role, Role.id == user_roles.c.role_id)
            .join(role_permissions, Role.id == role_permissions.c.role_id)
            .where(role_permissions.c.permission_id == permission_id)
            .options(selectinload(User.roles))
        )
        result = await self.session.scalars(stmt)
        return list(result.unique().all())

    async def exists_code(self, code: str) -> bool:
        stmt = select(func.count()).select_from(Permission).where(func.lower(Permission.code) == code.lower())
        return await self.session.scalar(stmt) > 0

    async def create(self, payload: PermissionCreate) -> Permission:
        new_code = await self._generate_next_code(Permission, "PRM")
        
        permission = Permission(
            code=new_code,
            description=payload.description,
            submenu_id=payload.submenu_id 
        )
        self.session.add(permission)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission