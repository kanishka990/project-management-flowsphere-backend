from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from app.core.rate_limiter import limiter

from app.utils.email import send_reset_password_email, send_verification_email
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    UserPasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserSelfRegister,
    EmailVerificationResponse,
)

from app.api.dependencies.auth_dependencies import get_user_service, get_current_active_user
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
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


@router.post("/forget-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/hour")
async def forget_password(
    request: Request,
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
):
    """
    Initiate a password reset flow for unauthenticated users.
    """
    token = await user_service.request_password_reset(payload.email)

    background_tasks.add_task(send_reset_password_email, payload.email, token)
    from app.core.config import get_settings
    response_data = {"detail": "Password reset instructions have been sent to your email."}
    if get_settings().DEBUG:
        response_data["token"] = token  # For development purposes only
    return response_data

@router.post("/reset-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/hour")
async def reset_password(
    request: Request,
    payload: PasswordResetConfirm,
    user_service: UserService = Depends(get_user_service),
):
    """
    Reset password using a token.
    """
    await user_service.reset_password(payload.token, payload.new_password)
    return {"detail": "Password has been reset successfully."}


@router.post("/register", response_model=EmailVerificationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")
async def register(
    request: Request,
    payload: UserSelfRegister,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
):
    """
    Self-register a new user.
    These users should not be forced to change password on first login.
    """
    _user, token = await user_service.create_user(
        payload,
        require_password_change=False,
    )
    if token:
        background_tasks.add_task(send_verification_email, payload.email, token)

    from app.core.config import get_settings
    response = EmailVerificationResponse(
        detail="Registration successful. Please check your email to verify your account."
    )
    if get_settings().DEBUG:
        response.token = token
    return response

@router.get("/verify-email", response_model=UserResponse)
async def verify_email(
    token: str,
    user_service: UserService = Depends(get_user_service),
):
    """
    Verify user's email using the token sent to their email.
    """
    user = await user_service.verify_email(token)
    return user
