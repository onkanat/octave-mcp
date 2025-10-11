"""
Pydantic request models for API endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field, validator
from models.entities import ResourceLimits


class RunRequest(BaseModel):
    """Request model for /run endpoint."""

    code: str = Field(..., description="Code to execute", min_length=1, max_length=50000)
    session_id: Optional[str] = Field(None, description="Session identifier", max_length=100)
    resource_limits: Optional[ResourceLimits] = Field(
        None, description="Optional resource limits overriding defaults"
    )

    @validator("code")
    def validate_code_content(cls, v):
        """Validate code content for basic security."""
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v


class PublishRequest(BaseModel):
    """Request model for /publish endpoint."""

    code: str = Field(..., description="Code to publish", min_length=1, max_length=50000)
    session_id: Optional[str] = Field(None, description="Session identifier", max_length=100)
    resource_limits: Optional[ResourceLimits] = Field(
        None, description="Optional resource limits overriding defaults"
    )

    @validator("code")
    def validate_code_content(cls, v):
        """Validate code content for basic security."""
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v


class GrabcodeRequest(BaseModel):
    """Request model for /grabcode endpoint."""

    share_id: str = Field(..., description="Share identifier", min_length=1, max_length=100)


class CleanupRequest(BaseModel):
    """Request model for /admin/cleanup endpoint."""

    dry_run: bool = Field(True, description="Perform dry run without actual deletion")
    force: bool = Field(False, description="Force delete (requires policy permission)")
    max_age_hours: Optional[int] = Field(None, description="Max age in hours", ge=1, le=8760)
    max_age_days: Optional[int] = Field(None, description="Max age in days", ge=1, le=365)
    session_id: Optional[str] = Field(
        None, description="Specific session to clean", max_length=100
    )

    @validator("max_age_days", "max_age_hours")
    def validate_age_settings(cls, v, values):
        """Ensure only one age setting is provided."""
        if v is not None and values.get("max_age_hours") is not None:
            if "max_age_days" in values and values["max_age_days"] is not None:
                raise ValueError("Cannot specify both max_age_hours and max_age_days")
        return v
