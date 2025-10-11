"""
Custom exceptions for the application.
"""

from typing import Any, Dict, Optional


class MCPException(Exception):
    """Base exception for MCP operations."""

    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(MCPException):
    """Input validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class SecurityError(MCPException):
    """Security-related errors."""

    def __init__(self, message: str, path: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, "SECURITY_ERROR", details)
        self.path = path


class ResourceError(MCPException):
    """Resource limit violations."""

    def __init__(self, message: str, resource_type: str, details: Optional[Dict] = None):
        super().__init__(message, "RESOURCE_ERROR", details)
        self.resource_type = resource_type


class ServiceError(MCPException):
    """External service errors (Octave, file system)."""

    def __init__(self, message: str, service: str, details: Optional[Dict] = None):
        super().__init__(message, "SERVICE_ERROR", details)
        self.service = service


class ExecutionError(MCPException):
    """Code execution errors."""

    def __init__(
        self,
        message: str,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        details: Optional[Dict] = None,
    ):
        super().__init__(message, "EXECUTION_ERROR", details)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class TimeoutError(MCPException):
    """Timeout errors."""

    def __init__(self, message: str, timeout_seconds: int, details: Optional[Dict] = None):
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.timeout_seconds = timeout_seconds


class NotFoundError(MCPException):
    """Resource not found errors."""

    def __init__(
        self, message: str, resource_type: str, resource_id: str, details: Optional[Dict] = None
    ):
        super().__init__(message, "NOT_FOUND_ERROR", details)
        self.resource_type = resource_type
        self.resource_id = resource_id
