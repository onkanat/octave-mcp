"""
Domain entities for the application.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, validator


class Session(BaseModel):
    """Domain model for user sessions."""

    session_id: str = Field(..., description="Unique session identifier")
    persistent: bool = Field(default=False, description="Whether session persists across restarts")
    start_time: datetime = Field(default_factory=datetime.now, description="Session start time")
    last_active: datetime = Field(default_factory=datetime.now, description="Last activity time")
    work_dir: Path = Field(..., description="Working directory for session")

    # Extended fields for session management
    description: Optional[str] = Field(None, description="Session description")
    created_at: float = Field(..., description="Creation timestamp")
    last_accessed: float = Field(..., description="Last access timestamp")
    run_count: int = Field(default=0, description="Number of runs executed")
    session_dir: Optional[str] = Field(None, description="Session directory path")

    @validator("work_dir", pre=True)
    def resolve_work_dir(cls, v):
        """Ensure work_dir is a Path object."""
        return Path(v) if not isinstance(v, Path) else v

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_active = datetime.now()

    class Config:
        arbitrary_types_allowed = True


class ResourceLimits(BaseModel):
    """Resource limits for code execution."""

    cpu_time_limit: Optional[int] = Field(None, description="CPU time limit in seconds")
    memory_limit_mb: Optional[int] = Field(None, description="Memory limit in MB")
    max_output_chars: int = Field(20000, description="Maximum output characters")
    max_image_size_bytes: int = Field(5 * 1024 * 1024, description="Maximum image size")
    timeout: int = Field(60, description="Execution timeout in seconds")

    @validator("cpu_time_limit", "memory_limit_mb", "timeout")
    def validate_positive_limits(cls, v):
        """Ensure limits are positive when specified."""
        if v is not None and v <= 0:
            raise ValueError("Resource limits must be positive")
        return v


class Run(BaseModel):
    """Domain model for code execution runs."""

    run_id: str = Field(..., description="Unique run identifier")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    code: str = Field(..., description="Executed code")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(..., description="Process exit code")
    runtime_seconds: float = Field(..., description="Execution time")
    created_at: datetime = Field(default_factory=datetime.now, description="Run creation time")
    resource_limits: ResourceLimits = Field(..., description="Applied resource limits")
    images: List[str] = Field(default_factory=list, description="Generated image paths")

    @property
    def success(self) -> bool:
        """Whether the run was successful."""
        return self.exit_code == 0

    @validator("runtime_seconds")
    def validate_runtime(cls, v):
        """Ensure runtime is non-negative."""
        if v < 0:
            raise ValueError("Runtime must be non-negative")
        return v


class Publish(BaseModel):
    """Domain model for published content."""

    publish_id: str = Field(..., description="Unique publish identifier")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    html_content: str = Field(..., description="Generated HTML content")
    html_size: int = Field(..., description="HTML content size")
    publish_dir: Path = Field(..., description="Directory where content is published")
    html_filename: str = Field(..., description="HTML filename")
    images: List[str] = Field(default_factory=list, description="Associated image paths")
    created_at: datetime = Field(default_factory=datetime.now, description="Publish creation time")
    warnings: List[str] = Field(default_factory=list, description="Publishing warnings")

    @validator("publish_dir", pre=True)
    def resolve_publish_dir(cls, v):
        """Ensure publish_dir is a Path object."""
        return Path(v) if not isinstance(v, Path) else v

    @validator("html_size")
    def validate_html_size(cls, v):
        """Ensure HTML size is non-negative."""
        if v < 0:
            raise ValueError("HTML size must be non-negative")
        return v

    class Config:
        arbitrary_types_allowed = True


class CleanupResult(BaseModel):
    """Domain model for cleanup operation results."""

    operation_id: str = Field(..., description="Unique operation identifier")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    deleted_runs: int = Field(default=0, description="Number of runs deleted")
    deleted_sessions: int = Field(default=0, description="Number of sessions deleted")
    errors: List[str] = Field(default_factory=list, description="Cleanup errors")
    started_at: datetime = Field(default_factory=datetime.now, description="Operation start time")
    completed_at: Optional[datetime] = Field(None, description="Operation completion time")

    def mark_completed(self) -> None:
        """Mark the cleanup operation as completed."""
        self.completed_at = datetime.now()


class PublishShare(BaseModel):
    """Domain model for published run sharing."""

    share_id: str = Field(..., description="Unique share identifier")
    run_id: str = Field(..., description="Associated run ID")
    title: str = Field(..., description="Publication title")
    description: Optional[str] = Field(None, description="Publication description")
    expires_at: float = Field(..., description="Expiration timestamp")
    created_at: float = Field(..., description="Creation timestamp")
    view_count: int = Field(default=0, description="Number of views")

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: float) -> float:
        """Validate expiration timestamp."""
        if v <= 0:
            raise ValueError("Expiration timestamp must be positive")
        return v

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: float) -> float:
        """Validate creation timestamp."""
        if v <= 0:
            raise ValueError("Creation timestamp must be positive")
        return v

    def is_expired(self) -> bool:
        """Check if publication has expired."""
        import time

        return time.time() > self.expires_at
