from uuid import UUID
from app.core.exceptions import ResourceNotFoundException
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_schema import (
    MenuCreate,
    MenuUpdate,
    NavigationResponse,
    NavigationMenuResponse,
    NavigationChildResponse,
)

class MenuService:
    def __init__(self, menu_repo: MenuRepository):
        self.menu_repo = menu_repo

    async def create_menu(self, payload: MenuCreate):
        return await self.menu_repo.create(payload)

    async def get_menu_by_id(self, menu_id: UUID):
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise ResourceNotFoundException("Menu")
        return menu

    async def list_menus(self):
        return await self.menu_repo.list()

    async def update_menu(self, menu_id: UUID, payload: MenuUpdate):
        menu = await self.get_menu_by_id(menu_id)
        updates = payload.model_dump(exclude_unset=True)
        return await self.menu_repo.update(menu, **updates)

    async def delete_menu(self, menu_id: UUID, deleted_by: UUID | None = None):
        menu = await self.get_menu_by_id(menu_id)
        await self.menu_repo.delete(menu, deleted_by=deleted_by)

    async def get_navigation(self, current_user) -> NavigationResponse:
        user_permission_codes = self._user_permission_codes(current_user)
        is_superadmin = self._is_superadmin(current_user)

        response_menus = []
        for menu in await self.menu_repo.list():
            if not self._is_visible_record(menu):
                continue

            children = [
                self._to_navigation_child(submenu)
                for submenu in self._visible_submenus(
                    menu.submenus,
                    user_permission_codes,
                    is_superadmin,
                )
            ]

            if children or menu.path:
                response_menus.append(
                    NavigationMenuResponse(
                        id=menu.id,
                        code=menu.code,
                        label=menu.name,
                        path=menu.path,
                        icon=menu.icon,
                        children=children,
                    )
                )

        return NavigationResponse(menus=response_menus)

    @staticmethod
    def _is_superadmin(user) -> bool:
        return any(
            (getattr(role, "name", "") or "").lower() == "superadmin"
            for role in getattr(user, "roles", []) or []
        )

    @staticmethod
    def _user_permission_codes(user) -> set[str]:
        return {
            permission.code.lower()
            for role in getattr(user, "roles", []) or []
            for permission in getattr(role, "permissions", []) or []
            if getattr(permission, "code", None)
        }

    @staticmethod
    def _submenu_permission_codes(submenu) -> set[str]:
        return {
            permission.code.lower()
            for permission in getattr(submenu, "permissions", []) or []
            if getattr(permission, "code", None)
        }

    @staticmethod
    def _is_visible_record(record) -> bool:
        return not getattr(record, "is_deleted", False) and getattr(record, "is_active", True)

    def _visible_submenus(
        self,
        submenus,
        user_permission_codes: set[str],
        is_superadmin: bool,
    ):
        sorted_submenus = sorted(
            submenus or [],
            key=lambda item: (getattr(item, "sort_order", 0), getattr(item, "title", "")),
        )

        for submenu in sorted_submenus:
            if not self._is_visible_record(submenu):
                continue
            if self._can_view_submenu(submenu, user_permission_codes, is_superadmin):
                yield submenu

    def _can_view_submenu(
        self,
        submenu,
        user_permission_codes: set[str],
        is_superadmin: bool,
    ) -> bool:
        if is_superadmin:
            return True
        submenu_permission_codes = self._submenu_permission_codes(submenu)
        return bool(user_permission_codes.intersection(submenu_permission_codes))

    @staticmethod
    def _to_navigation_child(submenu) -> NavigationChildResponse:
        return NavigationChildResponse(
            id=submenu.id,
            code=submenu.code,
            label=submenu.title,
            path=submenu.path,
            icon=submenu.icon,
        )
