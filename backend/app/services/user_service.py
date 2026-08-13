from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEmailException,
    DuplicatePhoneNumberException,
    ValidationException,
    ResourceNotFoundException,
    BadRequestException,
    RateLimitExceededException,
)
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.user_schema import (
    UserCreate,
    UserSelfRegister,
    UserUpdate,
)
from app.models.user_model import User
from app.models.role_model import Role

import secrets
import hashlib
from datetime import datetime, timedelta, UTC
from app.repositories.email_verification_token_repository import EmailVerificationTokenRepository
from app.models.email_verification_token_model import EmailVerificationToken
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.models.password_reset_token_model import PasswordResetToken

class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        email_verification_repo: EmailVerificationTokenRepository | None = None,
        password_reset_repo: PasswordResetTokenRepository | None = None,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.email_verification_repo = email_verification_repo
        self.password_reset_repo = password_reset_repo

    async def create_user(
        self,
        payload: UserCreate | UserSelfRegister,
        created_by: UUID | None = None,
        require_password_change: bool = False,
    ):
        if await self.user_repo.exists_email(payload.email):
            raise DuplicateEmailException()
        if await self.user_repo.exists_phone_number(payload.phone_number):
            raise DuplicatePhoneNumberException()

        hashed_password = await hash_password(payload.password)
        emp_id = await self.user_repo._generate_next_code(User, "emp_id", "EMP")

        # If it's self-registration (require_password_change=False), they are not active until verified
        is_active = require_password_change

        role_ids = payload.role_ids if isinstance(payload, UserCreate) else []
        roles = await self._get_roles_by_ids(role_ids)
        await self._validate_reporting_manager(
            reporting_manager_id=payload.reporting_manager_id,
        )

        user = await self.user_repo.create(
            user_data=payload,
            hashed_password=hashed_password,
            emp_id=emp_id,
            created_by=created_by,
            is_first_login=require_password_change,
            is_active=is_active,
            roles=roles,
        )

        loaded_user = await self.user_repo.get_by_id(user.id)
        if not loaded_user:
            raise ResourceNotFoundException("User")

        verification_token = None
        if not require_password_change and self.email_verification_repo:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            expires_at = datetime.now(UTC) + timedelta(hours=24)
            
            token_record = EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            await self.email_verification_repo.create(token_record)
            verification_token = raw_token

        return loaded_user, verification_token

    async def _get_roles_by_ids(self, role_ids: list[UUID]) -> list[Role]:
        if not role_ids:
            return []

        roles = await self.role_repo.get_by_ids(role_ids)
        roles_by_id = {role.id: role for role in roles}
        missing_role_ids = [
            str(role_id)
            for role_id in role_ids
            if role_id not in roles_by_id
        ]
        if missing_role_ids:
            raise ResourceNotFoundException(f"Role(s): {', '.join(missing_role_ids)}")

        return [roles_by_id[role_id] for role_id in role_ids]

    async def _validate_reporting_manager(
        self,
        reporting_manager_id: UUID | None,
        user_id: UUID | None = None,
    ) -> None:
        if reporting_manager_id is None:
            return

        if user_id is not None and reporting_manager_id == user_id:
            raise ValidationException("User cannot be their own reporting manager")

        manager = await self.user_repo.get_by_id(reporting_manager_id)
        if not manager:
            raise ResourceNotFoundException("Reporting manager")

    async def verify_email(self, raw_token: str):
        if not self.email_verification_repo:
            raise ValidationException("Email verification is not configured")

        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_record = await self.email_verification_repo.get_by_token_hash(token_hash)
        
        if not token_record or token_record.expires_at < datetime.now(UTC):
            raise ValidationException("Invalid or expired verification token")
        
        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user:
            raise ResourceNotFoundException("User")
            
        await self.user_repo.update(user, is_active=True)
        await self.email_verification_repo.update(token_record, used=True)
        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(UTC):
            raise BadRequestException(
                f"Account temporarily locked. Try again after {user.locked_until.strftime('%H:%M')} UTC"
            )

        if not await verify_password(password, user.hashed_password):
            # Increment failure count
            attempts = user.failed_login_attempts + 1
            updates = {"failed_login_attempts": attempts}
            if attempts >= 5:
                updates["locked_until"] = datetime.now(UTC) + timedelta(minutes=15)
            await self.user_repo.update(user, **updates)
            return None
        
        # Reset on success
        if user.failed_login_attempts > 0:
            await self.user_repo.update(user, failed_login_attempts=0, locked_until=None)

        return user

    async def change_password(self, user_id: UUID, current_password: str, new_password: str):
        user = await self.get_user_by_id(user_id)

        if not await verify_password(current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")

        return await self.user_repo.update(
            user,
            hashed_password=await hash_password(new_password),
            is_first_login=False,
        )

    async def request_password_reset(self, email: str) -> str:
        user = await self.user_repo.get_by_email_for_update(email)
        if not user:
            raise BadRequestException(
                "Email address not found. Please check the email address or register first."
            )
        if not user.is_active:
            raise BadRequestException(
                "This account is not active. Please verify your email before requesting a password reset."
            )
        
        if not self.password_reset_repo:
            raise ValidationException("Password reset is not configured")

        now = datetime.now(UTC)
        reset_request_window_started_at = now - timedelta(hours=1)
        recent_reset_request = await self.password_reset_repo.get_latest_request_for_user_since(
            user.id,
            reset_request_window_started_at,
        )
        if recent_reset_request:
            raise RateLimitExceededException(
                "Password reset can only be requested once per user every hour."
            )

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = now + timedelta(hours=1)
        
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.password_reset_repo.create(token_record)
        return raw_token

    async def reset_password(self, raw_token: str, new_password: str):
        if not self.password_reset_repo:
            raise ValidationException("Password reset is not configured")

        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_record = await self.password_reset_repo.get_by_token_hash(token_hash)
        
        if not token_record or token_record.expires_at < datetime.now(UTC):
            raise ValidationException("Invalid or expired password reset token")
            
        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user:
            raise ResourceNotFoundException("User")
            
        await self.user_repo.update(
            user,
            hashed_password=await hash_password(new_password),
            failed_login_attempts=0,
            locked_until=None
        )
        await self.password_reset_repo.update(token_record, used=True)
        return user

    async def get_user_by_id(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User")
        return user

    async def update_user(self, user_id: UUID, payload: UserUpdate):
        user = await self.user_repo.get_by_id_for_update(user_id)
        if not user:
            raise ResourceNotFoundException("User")

        update_data = payload.model_dump(exclude_unset=True)
        if "reporting_manager_id" in update_data:
            await self._validate_reporting_manager(
                reporting_manager_id=update_data["reporting_manager_id"],
                user_id=user_id,
            )

        await self.user_repo.update(user, **update_data)
        updated_user = await self.user_repo.get_by_id(user.id)
        if not updated_user:
            raise ResourceNotFoundException("User")
        return updated_user

    async def list_users(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        email: str | None = None,
        emp_id: str | None = None,
        is_active: bool | None = None,
        is_first_login: bool | None = None,
        role_id: UUID | None = None,
        department_id: UUID | None = None,
        reporting_manager_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        search_term = search or email or emp_id
        
        return await self.user_repo.list(
            page=page,
            page_size=page_size,
            search=search_term,
            is_active=is_active,
            is_first_login=is_first_login,
            role_id=role_id,
            department_id=department_id,
            reporting_manager_id=reporting_manager_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def list_project_managers(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
    ):
        role = await self.role_repo.get_by_name("Project Manager")
        if not role:
            return [], 0, page_size
            
        return await self.user_repo.list(
            page=page,
            page_size=page_size,
            search=search,
            role_id=role.id,
        )

    async def soft_delete_user(self, user_id: UUID, deleted_by: UUID | None = None):
        user = await self.get_user_by_id(user_id)
        await self.user_repo.soft_delete(user, user_id=str(deleted_by) if deleted_by else None)

    async def reactivate_user(self, user_id: UUID, reactivated_by: UUID | None = None):
        user = await self.user_repo.get_by_id_including_deleted(user_id)
        if not user:
            raise ResourceNotFoundException("User")
        if not user.is_deleted:
            raise BadRequestException("User is not deleted")

        await self.user_repo.reactivate(user, updated_by=reactivated_by)
        reactivated_user = await self.user_repo.get_by_id(user.id)
        if not reactivated_user:
            raise ResourceNotFoundException("User")
        return reactivated_user

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
