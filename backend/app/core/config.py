from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Backend API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    database_url: str = Field(
        default="mysql+aiomysql://user:password@localhost:3306/appdb",
        description="Database connection URL",
    )

    telegram_bot_token: str = Field(default="", description="Telegram bot token")
    telegram_webhook_url: str = Field(default="", description="Telegram webhook URL")

    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key for token signing",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=43200, description="JWT access token expiration in minutes (default: 30 days)"
    )

    sandbox_enabled: bool = Field(default=False, description="Enable sandbox mode")
    sandbox_api_url: str = Field(
        default="http://localhost:8080", description="Sandbox API URL"
    )


settings = Settings()


def get_settings() -> Settings:
    return settings
