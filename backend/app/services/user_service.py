from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEmailException,
    DuplicatePhoneNumberException,
    ValidationException,
    ResourceNotFoundException,
)
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
)
from app.models.user_model import User


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ):
        self.db = db
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def create_user(
        self,
        payload: UserCreate,
        created_by: UUID | None = None,
        require_password_change: bool = False,
    ):
        if await self.user_repo.exists_email(payload.email):
            raise DuplicateEmailException()
        if await self.user_repo.exists_phone_number(payload.phone_number):
            raise DuplicatePhoneNumberException()

        hashed_password = hash_password(payload.password)
        emp_id = await self.user_repo._generate_next_code(User, "EMP")

        user = await self.user_repo.create(
            user_data=payload,
            hashed_password=hashed_password,
            emp_id=emp_id,
            created_by=created_by,
            is_first_login=require_password_change,
        )
        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def change_password(self, user_id: UUID, current_password: str, new_password: str):
        user = await self.get_user_by_id(user_id)

        if not verify_password(current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")

        return await self.user_repo.update(
            user,
            hashed_password=hash_password(new_password),
            is_first_login=False,
        )

    async def get_user_by_id(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User")
        return user

    async def update_user(self, user_id: UUID, payload: UserUpdate):
        user = await self.get_user_by_id(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        return await self.user_repo.update(user, **update_data)

    async def list_users(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        email: str | None = None,
        emp_id: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        is_first_login: bool | None = None,
        role_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        search_term = search or email or emp_id
        
        return await self.user_repo.list(
            page=page,
            page_size=page_size,
            search=search_term,
            is_active=is_active,
            is_verified=is_verified,
            is_first_login=is_first_login,
            role_id=role_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def soft_delete_user(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        await self.user_repo.soft_delete(user)

    async def replace_roles(self, user_id: UUID, role_ids: list[UUID]):
        user = await self.get_user_by_id(user_id)
        roles = []
        for role_id in role_ids:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise ResourceNotFoundException(f"Role")
            roles.append(role)
            
        await self.user_repo.replace_roles(user, roles)
        return await self.user_repo.get_roles(user)

    async def get_user_roles(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.get_roles(user)

    async def get_user_permissions(self, user_id: UUID):
        await self.get_user_by_id(user_id)
        return await self.user_repo.get_permissions(user_id)