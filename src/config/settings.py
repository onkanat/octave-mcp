"""
Modern configuration management with Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration with environment variable support."""

    # API Configuration
    api_host: str = Field(default="127.0.0.1", description="API server host")
    api_port: int = Field(default=8000, description="API server port", ge=1, le=65535)

    # Rate Limiting
    rate_limit_max: int = Field(default=100, description="Max requests per window", ge=1)
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds", ge=1)

    # Resource Limits
    cpu_limit_seconds: Optional[int] = Field(default=30, description="CPU time limit", ge=1)
    memory_limit_mb: Optional[int] = Field(default=512, description="Memory limit in MB", ge=1)
    max_output_chars: int = Field(default=20000, description="Max output characters", ge=1)
    timeout_seconds: int = Field(default=60, description="Execution timeout", ge=1)
    max_image_size_bytes: int = Field(default=5 * 1024 * 1024, description="Max image size", ge=1)

    # File Paths
    runs_root: Path = Field(default=Path("runs"), description="Root directory for runs")
    tmpdir: Optional[Path] = Field(default=None, description="Temporary directory")
    retention_days: int = Field(default=0, description="File retention days", ge=0)
    publish_dir: str = Field(
        default="/tmp/octave_published", description="Published runs directory"
    )

    # URL settings
    base_url: str = Field(default="http://localhost:8000", description="Base URL for the service")

    # Octave Configuration
    octave_mode: str = Field(
        default="python", description="Execution mode", pattern="^(octave|python)$"
    )
    octave_bin: Optional[str] = Field(default=None, description="Octave binary path")
    fig_width: int = Field(default=620, description="Figure width", ge=1)
    fig_height: int = Field(default=480, description="Figure height", ge=1)

    # Security
    is_vision_model: bool = Field(default=False, description="Include image paths in response")
    allow_force_delete: bool = Field(default=False, description="Allow force delete operations")

    # Rate limiting
    rate_limit_max_requests: int = Field(default=100, description="Max requests per window")
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window in seconds")

    # Logging
    log_level: str = Field(
        default="INFO", description="Log level", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    @validator("runs_root", "tmpdir", pre=True)
    def resolve_paths(cls, v):
        """Resolve relative paths to absolute paths."""
        if v is None:
            return v
        return Path(v).resolve()

    @validator("tmpdir")
    def set_tmpdir_default(cls, v, values):
        """Set default tmpdir to runs_root if not specified."""
        if v is None:
            return values.get("runs_root")
        return v

    class Config:
        env_prefix = "MCP_"
        case_sensitive = False
        validate_assignment = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
