"""
Pydantic response models for API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImageResult(BaseModel):
    """Model for image results."""

    name: str = Field(..., description="Image filename")
    mime: str = Field(default="image/png", description="MIME type")
    b64: Optional[str] = Field(None, description="Base64 encoded image data")
    size: int = Field(..., description="Image size in bytes", ge=0)
    path: Optional[str] = Field(None, description="Image file path (vision mode only)")


class VectorizationWarning(BaseModel):
    """Model for vectorization analysis warnings."""

    lineno: int = Field(..., description="Line number", ge=1)
    col: int = Field(..., description="Column offset", ge=0)
    message: str = Field(..., description="Warning message")


class ErrorBlock(BaseModel):
    """Model for structured error information."""

    id: str = Field(..., description="Unique error identifier")
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    hint: Optional[str] = Field(None, description="Error hint for resolution")
    timestamp: datetime = Field(..., description="Error timestamp")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    run_id: Optional[str] = Field(None, description="Associated run ID")
    stdout_truncated: Optional[bool] = Field(None, description="Whether stdout was truncated")
    stderr_truncated: Optional[bool] = Field(None, description="Whether stderr was truncated")
    resource_violation: Optional[Dict[str, Any]] = Field(
        None, description="Resource violation details"
    )
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")


class RunResponse(BaseModel):
    """Response model for /run_octave endpoint."""

    success: bool = Field(..., description="Whether execution was successful")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(..., description="Process exit code")
    runtime_seconds: float = Field(..., description="Execution time in seconds", ge=0)
    images: List[ImageResult] = Field(default_factory=list, description="Generated images")
    vectorization_warnings: Optional[List[VectorizationWarning]] = Field(
        None, description="Vectorization analysis warnings"
    )
    error: Optional[ErrorBlock] = Field(None, description="Error information if failed")


class PublishResponse(BaseModel):
    """Response model for /publish endpoint."""

    html_b64: str = Field(..., description="Base64 encoded HTML content")
    html_truncated: bool = Field(default=False, description="Whether HTML was truncated")
    html_original_size: int = Field(..., description="Original HTML size in bytes", ge=0)
    publish_dir: str = Field(..., description="Directory where files were published")
    html_name: str = Field(..., description="HTML filename")
    images: List[str] = Field(default_factory=list, description="Relative paths to images")
    warnings: List[str] = Field(default_factory=list, description="Publishing warnings")
    error: Optional[str] = Field(None, description="Error message if failed")


class GrabcodeResponse(BaseModel):
    """Response model for /grabcode endpoint."""

    code: str = Field(default="", description="Retrieved code content")
    code_b64: str = Field(..., description="Base64 encoded code")
    line_count: int = Field(..., description="Number of lines in code", ge=0)
    warnings: List[str] = Field(default_factory=list, description="Retrieval warnings")


class CleanupError(BaseModel):
    """Model for cleanup operation errors."""

    path: Optional[str] = Field(None, description="Path that failed to clean")
    error: str = Field(..., description="Error message")


class CleanupResponse(BaseModel):
    """Response model for /admin/cleanup endpoint."""

    deleted_runs: int = Field(..., description="Number of runs deleted", ge=0)
    deleted_sessions: int = Field(..., description="Number of sessions deleted", ge=0)
    dry_run: bool = Field(..., description="Whether this was a dry run")
    errors: List[CleanupError] = Field(default_factory=list, description="Cleanup errors")


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: Optional[str] = Field(None, description="Application version")
    checks: Dict[str, bool] = Field(default_factory=dict, description="Individual health checks")
