from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.permissions import require_permission
from app.api.dependencies.auth_dependencies import get_current_active_user
from app.db.session import get_db
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserPasswordChange,
    UserRoleReplace,
    UserListResponse,
)
from app.schemas.role_schema import RoleResponse
from app.utils.pagination import PaginationParams, format_pagination_response
from app.schemas.permission_schema import PermissionResponse

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(
        db=db,
        user_repo=UserRepository(db),
        role_repo=RoleRepository(db),
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("users:create"))],
)
async def create_user(
    payload: UserCreate,
    current_user=Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(payload, created_by=current_user.id)


@router.get(
    "/",
    response_model=UserListResponse,
    dependencies=[Depends(require_permission("users:read"))],
)
async def list_users(
    search: str | None = Query(None),
    email: str | None = Query(None),       # Added for direct email lookup
    emp_id: str | None = Query(None),      # Added for direct employee ID lookup
    is_active: bool | None = Query(None),
    is_verified: bool | None = Query(None),
    is_first_login: bool | None = Query(None),
    role_id: UUID | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    user_service: UserService = Depends(get_user_service),
):
    items, total, actual_page_size = await user_service.list_users(
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
        email=email,
        emp_id=emp_id,
        is_active=is_active,
        is_verified=is_verified,
        is_first_login=is_first_login,
        role_id=role_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return format_pagination_response(items, pagination.page, actual_page_size, total)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def get_my_profile(
    current_user=Depends(get_current_active_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def update_my_profile(
    payload: UserUpdate,
    current_user=Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(current_user.id, payload)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users:read"))],
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users:update"))],
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    # This single endpoint now handles generic updates AND activation/verification toggles
    return await user_service.update_user(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("users:delete"))],
)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.soft_delete_user(user_id)
    return {}


@router.put(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("users:update"))],
)
async def replace_roles(
    user_id: UUID,
    payload: UserRoleReplace,
    user_service: UserService = Depends(get_user_service),
):
    # The frontend will send the complete array of role_ids to sync
    return await user_service.replace_roles(user_id, payload.role_ids)


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("users:read"))],
)
async def get_user_roles(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_roles(user_id)


@router.get(
    "/{user_id}/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("users:read"))],
)
async def get_user_permissions(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_permissions(user_id)