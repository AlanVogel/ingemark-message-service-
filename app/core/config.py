from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = "postgresql+asyncpg://ingemark:ingemark@db:5432/ingemark"
    echo: bool = False

    model_config = {"env_prefix": "DB_"}


class AuthConfig(BaseSettings):
    api_key: str = "change-me-in-production"

    model_config = {"env_prefix": "AUTH_"}


class SwaggerConfig(BaseSettings):
    username: str = "admin"
    password: str = "admin"

    model_config = {"env_prefix": "SWAGGER_"}


class AppConfig:
    """Central configuration access point.

    Usage:
        from app.core.config import config
        config.DATABASE.url
        config.AUTH.api_key
        config.SWAGGER.username
    """

    DATABASE = DatabaseConfig()
    AUTH = AuthConfig()
    SWAGGER = SwaggerConfig()


config = AppConfig()
