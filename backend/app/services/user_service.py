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

    async def generate_employee_id(self) -> str:
        number = await self.user_repo.get_next_employee_sequence()
        return f"EMP{number:06d}"

    async def create_user(self, payload: UserCreate, created_by: UUID | None = None):
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
        )
        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_id(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User")
        return user

    async def get_user_by_email(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ResourceNotFoundException("User")
        return user

    async def get_user_by_emp_id(self, emp_id: str):
        user = await self.user_repo.get_by_emp_id(emp_id)
        if not user:
            raise ResourceNotFoundException("User")
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        is_first_login: bool | None = None,
        role_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        return await self.user_repo.list(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
            is_verified=is_verified,
            is_first_login=is_first_login,
            role_id=role_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_user(self, user_id: UUID, payload: UserUpdate):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.update(
            user,
            first_name=payload.first_name,
            middle_name=payload.middle_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
        )

    async def soft_delete_user(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        await self.user_repo.soft_delete(user)
        return True

    async def activate_user(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.update(user, is_active=True)

    async def deactivate_user(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.update(user, is_active=False)

    async def verify_user(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.update(user, is_verified=True)

    async def change_password(self, user_id: UUID, current_password: str, new_password: str):
        user = await self.get_user_by_id(user_id)
        if not verify_password(current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")
        return await self.user_repo.update(user, hashed_password=hash_password(new_password))

    async def assign_role(self, user_id: UUID, role_id: UUID):
        user = await self.get_user_by_id(user_id)
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise ResourceNotFoundException("Role")
        await self.user_repo.assign_role(user, role)
        return role

    async def reset_password(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        # In a full implementation, generate a reset token and send an email.
        return None

    async def remove_role(self, user_id: UUID, role_id: UUID):
        user = await self.get_user_by_id(user_id)
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise ResourceNotFoundException("Role")
        await self.user_repo.remove_role(user, role)
        return role

    async def replace_roles(self, user_id: UUID, role_ids: list[UUID]):
        user = await self.get_user_by_id(user_id)
        roles = []
        for role_id in role_ids:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise ResourceNotFoundException("Role")
            roles.append(role)
        await self.user_repo.replace_roles(user, roles)
        return roles

    async def get_user_roles(self, user_id: UUID):
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.get_roles(user)

    async def get_user_permissions(self, user_id: UUID):
        return await self.user_repo.get_permissions(user_id)
    
    