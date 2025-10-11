"""
Modern security utilities for path validation and sanitization.
"""

from pathlib import Path
from typing import Union

from exceptions import SecurityError


def validate_path_security(path: Union[str, Path]) -> Path:
    """
    Validate path for security issues.

    Args:
        path: Path to validate

    Returns:
        Validated Path object

    Raises:
        SecurityError: If path is unsafe
    """
    path_obj = Path(path)

    # Check for path traversal
    if ".." in str(path_obj):
        raise SecurityError("Path traversal detected", "path_validation", {"path": str(path)})

    # For absolute paths, restrict to safe directories
    if path_obj.is_absolute():
        resolved_path = path_obj.resolve()
        if not (
            str(resolved_path).startswith("/tmp")
            or str(resolved_path).startswith("/private/tmp")
            or
            # Allow paths in current working directory for development
            str(resolved_path).startswith(str(Path.cwd()))
        ):
            raise SecurityError(
                "Absolute path not allowed outside safe directories",
                "path_validation",
                {"path": str(path)},
            )
        return resolved_path

    # For relative paths, resolve and return
    return path_obj.resolve()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem operations.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove dangerous characters
    dangerous_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    sanitized = filename

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def ensure_safe_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory is safe for operations.

    Args:
        directory: Directory path

    Returns:
        Validated directory Path

    Raises:
        SecurityError: If directory is unsafe
    """
    dir_path = validate_path_security(directory)

    # Create if doesn't exist
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise SecurityError(
            "Permission denied creating directory",
            "directory_creation",
            {"directory": str(dir_path)},
        )

    return dir_path
