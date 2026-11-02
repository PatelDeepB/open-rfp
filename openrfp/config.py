"""Configuration settings for OpenRFP."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    data_dir: Path = Path("./data/storage")

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    retrieval_top_k: int = 5
    similarity_threshold: float = 0.50

    confidence_green: float = 0.80
    confidence_amber: float = 0.50

    def ensure_data_directory(self) -> Path:
        """Ensure the local storage directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir


settings = Settings()
