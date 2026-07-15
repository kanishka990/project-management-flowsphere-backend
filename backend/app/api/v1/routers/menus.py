from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.permissions import PermissionChecker
from app.api.dependencies.auth_dependencies import get_current_active_user
from app.models.user_model import User
from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService
from app.schemas.menu_schema import (
    MenuCreate,
    MenuResponse,
    MenuUpdate,
    NavigationResponse
)

router = APIRouter(prefix="/menus", tags=["Menus"])

def get_menu_service(db: AsyncSession = Depends(get_db)) -> MenuService:
    return MenuService(MenuRepository(db))

@router.post(
    "/", 
    response_model=MenuResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["menus:create"]))]
)
async def create_menu(payload: MenuCreate, service: MenuService = Depends(get_menu_service)):
    return await service.create_menu(payload)

@router.get(
    "/", 
    response_model=list[MenuResponse],
    dependencies=[Depends(PermissionChecker(["menus:read"]))]
)
async def list_menus(service: MenuService = Depends(get_menu_service)):
    return await service.list_menus()

@router.get(
    "/navigation",
    response_model=NavigationResponse,
    description="Returns a dynamically generated navigation menu based on the current user's permissions."
)
async def get_user_navigation(
    service: MenuService = Depends(get_menu_service),
    current_user: User = Depends(get_current_active_user),
):
    return await service.get_navigation(current_user)

@router.patch(
    "/{menu_id}", 
    response_model=MenuResponse,
    dependencies=[Depends(PermissionChecker(["menus:update"]))]
)
async def update_menu(menu_id: UUID, payload: MenuUpdate, service: MenuService = Depends(get_menu_service)):
    return await service.update_menu(menu_id, payload)

@router.delete(
    "/{menu_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["menus:delete"]))]
)
async def delete_menu(menu_id: UUID, service: MenuService = Depends(get_menu_service)):
    await service.delete_menu(menu_id)
    return {}
