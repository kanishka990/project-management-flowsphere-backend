from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.services.permission_service import PermissionService
from app.schemas.permission_schema import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    PermissionListResponse,
)
from app.schemas.user_schema import UserResponse
from app.schemas.role_schema import RoleResponse 
from app.utils.pagination import PaginationParams, format_pagination_response

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(
        db=db,
        permission_repo=PermissionRepository(db),
        role_repo=RoleRepository(db),
    )


@router.post(
    "/",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["permissions:create"]))],
)
async def create_permission(
    payload: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
):
    return await service.create_permission(payload)


@router.get(
    "/",
    response_model=PermissionListResponse,
    dependencies=[Depends(PermissionChecker(["permissions:read"]))],
)
async def list_permissions(
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: PermissionService = Depends(get_permission_service),
):
    items, total, actual_page_size = await service.list_permissions(
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return format_pagination_response(items, pagination.page, actual_page_size, total)


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(PermissionChecker(["permissions:read"]))],
)
async def get_permission(
    permission_id: UUID,
    service: PermissionService = Depends(get_permission_service),
):
    return await service.get_permission_by_id(permission_id)


@router.patch(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(PermissionChecker(["permissions:update"]))],
)
async def update_permission(
    permission_id: UUID,
    payload: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
):
    return await service.update_permission(permission_id, payload)


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["permissions:delete"]))],
)
async def delete_permission(
    permission_id: UUID,
    service: PermissionService = Depends(get_permission_service),
):
    await service.delete_permission(permission_id)
    return {}


@router.get(
    "/{permission_id}/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(PermissionChecker(["permissions:read"]))],
)
async def get_roles_for_permission(
    permission_id: UUID,
    service: PermissionService = Depends(get_permission_service),
):
    return await service.get_roles(permission_id)


@router.get(
    "/{permission_id}/users",
    response_model=list[UserResponse],
    dependencies=[Depends(PermissionChecker(["permissions:read"]))],
)
async def get_users_for_permission(
    permission_id: UUID,
    service: PermissionService = Depends(get_permission_service),
):
    return await service.get_users(permission_id)