from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kinetiq API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
