from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.permissions import require_permission
from app.db.session import get_db
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.services.role_service import RoleService
from app.schemas.role_schema import RoleCreate, RoleResponse, RoleUpdate, RoleListResponse
from app.schemas.permission_schema import PermissionResponse
from app.schemas.role_schema import RolePermissionReplace
from app.schemas.user_schema import UserResponse
from app.utils.pagination import PaginationParams, format_pagination_response

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(
        db=db,
        role_repo=RoleRepository(db),
        permission_repo=PermissionRepository(db),
    )


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("roles:create"))],
)
async def create_role(
    payload: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    return await service.create_role(payload)


@router.get(
    "/",
    response_model=RoleListResponse,
    dependencies=[Depends(require_permission("roles:read"))],
)
async def list_roles(
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: RoleService = Depends(get_role_service),
):
    items, total, actual_page_size = await service.list_roles(
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return format_pagination_response(items, pagination.page, actual_page_size, total)


@router.get(
    "/search",
    response_model=RoleListResponse,
    dependencies=[Depends(require_permission("roles:read"))],
)
async def search_roles(
    q: str = Query(..., min_length=1),
    pagination: PaginationParams = Depends(PaginationParams),
    service: RoleService = Depends(get_role_service),
):
    items, total, actual_page_size = await service.list_roles(
        search=q,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return format_pagination_response(items, pagination.page, actual_page_size, total)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("roles:read"))],
)
async def get_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_role_by_id(role_id)


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("roles:update"))],
)
async def update_role(
    role_id: int,
    payload: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(role_id, payload)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("roles:delete"))],
)
async def delete_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    await service.delete_role(role_id)
    return {}


@router.post(
    "/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("roles:update"))],
)
async def assign_permission(
    role_id: int,
    permission_id: int,
    service: RoleService = Depends(get_role_service),
):
    await service.assign_permission(role_id, permission_id)
    return {}


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("roles:update"))],
)
async def remove_permission(
    role_id: int,
    permission_id: int,
    service: RoleService = Depends(get_role_service),
):
    await service.remove_permission(role_id, permission_id)
    return {}


@router.put(
    "/{role_id}/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("roles:update"))],
)
async def replace_permissions(
    role_id: int,
    payload: RolePermissionReplace,
    service: RoleService = Depends(get_role_service),
):
    return await service.replace_permissions(role_id, payload.permission_ids)


@router.get(
    "/{role_id}/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("roles:read"))],
)
async def get_permissions(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_permissions(role_id)


@router.get(
    "/{role_id}/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission("roles:read"))],
)
async def get_users_in_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_users(role_id)