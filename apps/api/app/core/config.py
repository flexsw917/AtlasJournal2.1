from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ZellaLite API"
    api_v1_prefix: str = "/"
    secret_key: str = Field(default="change-me", env="SECRET_KEY")
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    jwt_algorithm: str = "HS256"
    sqlite_path: Path = Field(default=Path("data/zellalite.db"), env="SQLITE_PATH")
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], env="ALLOWED_ORIGINS")
    uploads_dir: Path = Field(default=Path("uploads"), env="UPLOADS_DIR")
    max_upload_size: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
