from fastapi import APIRouter, Depends, status
from uuid import UUID
from app.api.dependencies.permissions import require_permission
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService
from app.schemas.menu_schema import MenuCreate, MenuResponse, MenuUpdate

router = APIRouter(prefix="/menus", tags=["Menus"])

def get_menu_service(db: AsyncSession = Depends(get_db)) -> MenuService:
    return MenuService(db, MenuRepository(db))

@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(payload: MenuCreate, service: MenuService = Depends(get_menu_service)):
    return await service.create_menu(payload)

@router.get("/", response_model=list[MenuResponse])
async def list_menus(service: MenuService = Depends(get_menu_service)):
    return await service.list_menus()

@router.patch("/{menu_id}", response_model=MenuResponse)
async def update_menu(menu_id: UUID, payload: MenuUpdate, service: MenuService = Depends(get_menu_service)):
    return await service.update_menu(menu_id, payload)

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(menu_id: UUID, service: MenuService = Depends(get_menu_service)):
    await service.delete_menu(menu_id)
    return {}