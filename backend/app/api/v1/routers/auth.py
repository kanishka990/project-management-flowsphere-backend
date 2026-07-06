from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token, create_refresh_token
from app.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    UserPasswordChange,
    PasswordResetRequest,
)

from app.api.dependencies.auth_dependencies import get_user_service, get_current_active_user
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Authenticate a user and return JWT access + refresh tokens.
    If the user is logging in for the first time with a temporary password,
    return a flag prompting them to change it.
    """
    user = await user_service.authenticate_user(
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(str(user.id))

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        require_password_change=user.is_first_login,
        message="Password change required on first login" if user.is_first_login else None,
    )


@router.put("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
    payload: UserPasswordChange,
    current_user=Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update password for the currently authenticated user.
    """
    await user_service.change_password(
        user_id=current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"detail": "Password changed successfully."}


@router.post("/reset-password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    payload: PasswordResetRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Initiate a password reset flow for unauthenticated users.
    """
    await user_service.reset_password(payload.email)
    return {"detail": "If the email exists, password reset instructions have been sent."}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Self-register a new user.
    These users should not be forced to change password on first login.
    """
    user = await user_service.create_user(
        payload,
        require_password_change=False,
    )
    return user