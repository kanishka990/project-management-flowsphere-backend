from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.permissions import router as permissions_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.db.health import check_database
from app.api.v1.routers.menus import router as menus_router
from app.api.v1.routers.submenus import router as submenus_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown context.
    """
    db_ok = await check_database()
    if not db_ok:
        raise RuntimeError("Failed to connect to PostgreSQL database")
    yield


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Resource Management System Backend API",
        lifespan=lifespan,
    )

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(roles_router, prefix="/api/v1")
    app.include_router(permissions_router, prefix="/api/v1")
    app.include_router(menus_router, prefix="/api/v1")
    app.include_router(submenus_router, prefix="/api/v1")

    app.add_exception_handler(AppException, app_exception_handler)

    add_middleware(app, settings)
    add_basic_routes(app)

    return app


async def app_exception_handler(request: Request, exc: AppException):
    """
    Global handler for application-level exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def add_middleware(app: FastAPI, settings):
    """
    Configure middleware for the application.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        max_age=settings.CORS_MAX_AGE,
    )


def add_basic_routes(app: FastAPI) -> None:
    """
    Add root and health-related utility endpoints.
    """
    @app.get("/")
    async def root():
        return {
            "message": f"{get_settings().APP_NAME} is running",
            "version": "1.0.0",
        }

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}


app = create_app()