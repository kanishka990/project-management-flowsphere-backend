from fastapi import Depends
from app.api.dependencies.auth_dependencies import get_current_active_user
from app.core.exceptions import PermissionDeniedException

def require_permission(permission_code: str):
    def dependency(current_user=Depends(get_current_active_user)):
        if any((role.name or "").lower() == "superadmin" for role in (current_user.roles or [])):
            return current_user

        user_permissions = {
            perm.code.lower()
            for role in (current_user.roles or [])
            for perm in (role.permissions or [])
        }

        if permission_code.lower() not in user_permissions:
            raise PermissionDeniedException(
                detail=f"Missing required permission: {permission_code}"
            )

        return current_user

    return dependency