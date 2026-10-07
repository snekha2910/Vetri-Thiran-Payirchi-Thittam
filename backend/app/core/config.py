import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "PocketSmart AI Backend"
    environment: str = "development"
    port: int = 8000
    debug: bool = True

    # Supabase credentials
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Google Gemini AI credentials
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_timeout: int = 60
    gemini_mock_mode: bool = False
    product_provider_mode: str = "mock"

    # CORS configuration
    cors_origins: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return [i.strip().rstrip("/") for i in v if isinstance(i, str) and i.strip()]
        return v

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ("development", "test", "dev")

settings = Settings()
