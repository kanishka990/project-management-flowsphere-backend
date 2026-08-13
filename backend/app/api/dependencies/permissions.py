from fastapi import Depends
from app.api.dependencies.auth_dependencies import get_current_active_user
from app.core.exceptions import PermissionDeniedException

class PermissionChecker:
    def __init__(self, required_permissions: list[str], match_all: bool = True):
        self.required_permissions = [p.lower() for p in required_permissions]
        self.match_all = match_all

    async def __call__(self, current_user=Depends(get_current_active_user)):
        if any((role.name or "").lower() == "superadmin" for role in (current_user.roles or [])):
            return current_user

        user_permissions = {
            perm.code.lower()
            for role in (current_user.roles or [])
            for perm in (role.permissions or [])
        }

        if self.match_all:
            missing_permissions = [p for p in self.required_permissions if p not in user_permissions]
            if missing_permissions:
                raise PermissionDeniedException(
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                )
        else:
            if not any(p in user_permissions for p in self.required_permissions):
                raise PermissionDeniedException(
                    detail=f"At least one of the following permissions is required: {', '.join(self.required_permissions)}"
                )

        return current_user