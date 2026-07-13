from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.submenu_repository import SubMenuRepository
from app.services.submenu_service import SubMenuService
from app.schemas.submenu_schema import SubMenuCreate, SubMenuResponse, SubMenuUpdate

router = APIRouter(prefix="/submenus", tags=["SubMenus"])

def get_submenu_service(db: AsyncSession = Depends(get_db)) -> SubMenuService:
    return SubMenuService(SubMenuRepository(db))

@router.post(
    "/", 
    response_model=SubMenuResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["submenus:create"]))]
)
async def create_submenu(payload: SubMenuCreate, service: SubMenuService = Depends(get_submenu_service)):
    return await service.create_submenu(payload)

@router.get(
    "/", 
    response_model=list[SubMenuResponse],
    dependencies=[Depends(PermissionChecker(["submenus:read"]))]
)
async def list_submenus(menu_id: UUID | None = Query(None), service: SubMenuService = Depends(get_submenu_service)):
    return await service.list_submenus(menu_id=menu_id)

@router.delete(
    "/{submenu_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["submenus:delete"]))]
)
async def delete_submenu(submenu_id: UUID, service: SubMenuService = Depends(get_submenu_service)):
    await service.delete_submenu(submenu_id)
    return {}


