from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PMO项目管理系统"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "pmo-system-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8小时

    DATABASE_URL: str = "sqlite:///./pmo.db"

    class Config:
        env_file = ".env"


settings = Settings()
