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