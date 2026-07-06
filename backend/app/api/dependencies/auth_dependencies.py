from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.repositories.role_repository import RoleRepository
from app.core.exceptions import AppException

security = HTTPBearer()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(
        db=db,
        user_repo=UserRepository(db),
        role_repo=RoleRepository(db),
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service),
):
    try:
        payload = decode_access_token(credentials.credentials)
    except (HTTPException, AppException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_emp_id = payload.get("sub")
    if not user_emp_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await user_service.user_repo.get_by_emp_id(user_emp_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found"
        )
        
    return user

async def get_current_active_user(
    user=Depends(get_current_user),
):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user