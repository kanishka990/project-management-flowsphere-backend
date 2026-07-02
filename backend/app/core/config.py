from sqlalchemy import URL
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    APP_NAME: str = Field(..., min_length=1)
    DEBUG: bool = False

    # Database
    DB_HOST: str = Field(..., min_length=1)
    DB_PORT: int = Field(5432, ge=1, le=65535)
    DB_NAME: str = Field(..., min_length=1)
    DB_USER: str = Field(..., min_length=1)
    DB_PASSWORD: SecretStr = Field(..., min_length=1)

    # JWT
    JWT_SECRET_KEY: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, ge=1, le=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, ge=1, le=7)

    # CORS / middleware
    CORS_ALLOW_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_MAX_AGE: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",
        case_sensitive=True,
    )

    @property
    def DATABASE_URL(self) -> str:
        url = URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )
        return url.render_as_string(hide_password=False)
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()