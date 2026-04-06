"""Application settings and environment configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from defaults and environment variables."""

    PROJECT_NAME: str = "Kinetiq API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True

    @staticmethod
    def _split_csv(value: str) -> list[str]:
        """Convert a comma-separated string into a cleaned list of values."""
        value = value.strip()
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_allow_origins_list(self) -> list[str]:
        """Return allowed CORS origins as a list."""
        return self._split_csv(self.CORS_ALLOW_ORIGINS)

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Return allowed CORS methods as a list."""
        return self._split_csv(self.CORS_ALLOW_METHODS)

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Return allowed CORS headers as a list."""
        return self._split_csv(self.CORS_ALLOW_HEADERS)

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
