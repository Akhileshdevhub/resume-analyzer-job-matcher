"""Application configuration.

All settings are read from environment variables (or a local `.env` file) and
validated once at startup by pydantic-settings. Centralising configuration here
means no other module ever calls `os.environ` directly, and every setting has a
documented default so the app runs with an empty environment.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # pydantic-settings looks for a .env file and ignores unknown keys.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ---- Server ----
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed frontend origins.",
    )

    # ---- Uploads ----
    max_upload_mb: int = Field(default=5, description="Max resume upload size (MB).")

    # ---- Semantic engine ----
    # auto | tfidf | embeddings
    semantic_backend: str = Field(default="auto")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")

    # ---- Persistence ----
    enable_history: bool = Field(default=True)
    database_url: str = Field(default="sqlite:///./resume_matcher.sqlite3")

    # ---- LLM (optional) ----
    llm_provider: str = Field(default="", description="'openai', 'anthropic', or '' to disable.")
    llm_model: str = Field(default="")
    llm_api_key: str = Field(default="")
    llm_timeout_seconds: int = Field(default=30)

    # ---- Derived helpers ----
    @property
    def cors_origin_list(self) -> list[str]:
        """Split the comma-separated origins into a clean list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def llm_enabled(self) -> bool:
        """True only when a provider and key are both configured."""
        return bool(self.llm_provider.strip()) and bool(self.llm_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (parsed once per process)."""
    return Settings()
