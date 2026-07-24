from __future__ import annotations

from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_model import User
from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.associations_model import user_roles, role_permissions
from app.schemas.user_schema import UserCreateBase
from app.utils.pagination import paginate
from app.repositories.base_repository import BaseRepository  

class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.is_deleted == False).options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.reporting_manager),
            selectinload(User.department),
        )
        return await self.session.scalar(stmt)

    async def get_by_id_for_update(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.is_deleted == False)
            .with_for_update()
        )
        return await self.session.scalar(stmt)

    async def get_by_id_including_deleted(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id).options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.reporting_manager),
            selectinload(User.department),
        )
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        normalized = email.lower()
        stmt = select(User).where(func.lower(User.email) == normalized, User.is_deleted == False).options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.reporting_manager),
            selectinload(User.department),
        )
        return await self.session.scalar(stmt)

    async def get_by_email_for_update(self, email: str) -> User | None:
        normalized = email.lower()
        stmt = (
            select(User)
            .where(func.lower(User.email) == normalized, User.is_deleted == False)
            .with_for_update()
        )
        return await self.session.scalar(stmt)

    async def get_by_emp_id(self, emp_id: str) -> User | None:
        stmt = select(User).where(User.emp_id == emp_id, User.is_deleted == False).options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.reporting_manager),
            selectinload(User.department),
        )
        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int, 
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None,
        is_first_login: bool | None = None,
        role_id: UUID | None = None,
        department_id: UUID | None = None,
        reporting_manager_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ): 
        stmt = select(User).where(User.is_deleted == False).options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.reporting_manager),
            selectinload(User.department),
        )

        if search:
            query_expr = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.emp_id).like(query_expr),
                    func.lower(User.email).like(query_expr),
                    func.lower(User.full_name).like(query_expr),
                    func.lower(User.phone_number).like(query_expr),
                )
            )

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        if is_first_login is not None:
            stmt = stmt.where(User.is_first_login == is_first_login)

        if role_id is not None:
            stmt = stmt.join(user_roles).where(user_roles.c.role_id == role_id)

        if department_id is not None:
            stmt = stmt.where(User.department_id == department_id)

        if reporting_manager_id is not None:
            stmt = stmt.where(User.reporting_manager_id == reporting_manager_id)

        sort_mapping = {
            "created_at": User.created_at,
            "updated_at": User.updated_at,
            "emp_id": User.emp_id,
            "full_name": User.full_name,
        }
        stmt = self._apply_sorting(stmt, User, sort_by, sort_order, sort_mapping)
        
        return await paginate(
            session=self.session, 
            statement=stmt, 
            page=page, 
            page_size=page_size
        )

    async def create(
        self,
        user_data: UserCreateBase,
        hashed_password: str,
        emp_id: str,
        created_by=None,
        is_first_login: bool | None = None,
        is_active: bool = True,
        roles: list[Role] | None = None,
    ) -> User:
        user = User(
            emp_id=emp_id,
            email=user_data.email.lower(),
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            hashed_password=hashed_password,
            created_by=created_by,
            updated_by=created_by,
            is_active=is_active,
            is_first_login=True if is_first_login is None else is_first_login,
            department_id=user_data.department_id,
            reporting_manager_id=user_data.reporting_manager_id,
            roles=roles or [],
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    _UPDATABLE_FIELDS = frozenset({
        "full_name", "phone_number", "department_id", "reporting_manager_id",
        "is_active", "is_first_login", "hashed_password", "updated_by",
        "is_deleted", "deleted_at", "deleted_by",
        "failed_login_attempts", "locked_until",
    })

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if key in self._UPDATABLE_FIELDS:
                setattr(user, key, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def soft_delete(self, user: User, user_id: str | None = None) -> None:
        user.is_active = False
        await super().soft_delete(user, user_id)

    async def reactivate(self, user: User, updated_by: UUID | None = None) -> User:
        user.is_deleted = False
        user.deleted_at = None
        user.deleted_by = None
        user.is_active = True
        user.updated_by = updated_by
        await self.session.flush()
        return user

    async def exists_email(self, email: str) -> bool:
        normalized = email.lower()
        stmt = select(func.count()).select_from(User).where(func.lower(User.email) == normalized, User.is_deleted == False)
        return await self.session.scalar(stmt) > 0

    async def exists_phone_number(self, phone_number: str) -> bool:
        stmt = select(func.count()).select_from(User).where(User.phone_number == phone_number, User.is_deleted == False)
        return await self.session.scalar(stmt) > 0
    
    async def exists_emp_id(self, emp_id: str) -> bool:
        stmt = select(func.count()).select_from(User).where(User.emp_id == emp_id, User.is_deleted == False)
        return await self.session.scalar(stmt) > 0

    async def assign_role(self, user: User, role: Role) -> None:
        if role in user.roles:
            return
        user.roles.append(role)
        await self.session.flush()

    async def remove_role(self, user: User, role: Role) -> None:
        if role in user.roles:
            user.roles.remove(role)
            await self.session.flush()

    async def replace_roles(self, user: User, roles: list[Role]) -> None:
        user.roles = roles
        await self.session.flush()

    async def get_roles(self, user: User) -> list[Role]:
        return user.roles

    async def get_permissions(self, user_id: UUID) -> list[Permission]:
        stmt = (
            select(Permission)
            .join(role_permissions)
            .join(Role)
            .join(user_roles)
            .where(user_roles.c.user_id == user_id)
            .options(selectinload(Permission.roles))
        )
        result = await self.session.scalars(stmt)
        return result.unique().all()

    async def user_has_permission(self, user_id: UUID, permission_code: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(Permission)
            .join(role_permissions)
            .join(Role)
            .join(user_roles)
            .where(user_roles.c.user_id == user_id)
            .where(func.lower(Permission.code) == permission_code.lower())
        )
        return await self.session.scalar(stmt) > 0
