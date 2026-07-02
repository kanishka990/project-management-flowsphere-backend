from fastapi import status


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class AuthenticationException(AppException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired."""
    def __init__(self):
        super().__init__(detail="Token has expired")


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""
    def __init__(self):
        super().__init__(detail="Invalid token")


class ResourceNotFoundException(AppException):
    """Raised when resource not found."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            detail=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateEmailException(AppException):
    """Raised when email already exists."""
    def __init__(self):
        super().__init__(
            detail="Email already registered",
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationException(AppException):
    """Raised when validation fails."""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

class PermissionDeniedException(AppException):
    """Raised when an authenticated user lacks required privileges."""
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class BadRequestException(AppException):
    """Raised for business logic errors, separate from 422 schema validation."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ResourceConflictException(AppException):
    """Raised for general database or state conflicts (e.g., Foreign Key violations)."""
    def __init__(self, detail: str = "Resource state conflict"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitExceededException(AppException):
    """Raised when a user exceeds their API quota."""
    def __init__(self):
        super().__init__(
            detail="Too many requests, please try again later",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ExternalServiceException(AppException):
    """Raised when a third-party API (Stripe, AWS, etc.) fails."""
    def __init__(self, service_name: str = "External service"):
        super().__init__(
            detail=f"{service_name} is currently unavailable",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )