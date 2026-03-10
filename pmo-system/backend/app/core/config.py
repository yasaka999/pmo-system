from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PMO项目管理系统"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "pmo-system-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8小时

    # 默认使用 PostgreSQL（支持高并发），SQLite 仅用于开发测试
    DATABASE_URL: str = "postgresql://pmo_user:pmo_secure_2026@localhost:5432/pmo_db"

    class Config:
        env_file = ".env"


settings = Settings()
