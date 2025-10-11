"""
Secure file I/O adapter for OctaveMCP with strict access control.

This module provides safe read_file and write_file operations that:
- Enforce directory whitelist (only MCP_RUNS_ROOT/TMPDIR access)
- Resolve symlinks and validate targets
- Apply size limits (2000 chars text, 5MB binary)
- Generate MCP-compliant error blocks
- Log security violations

Used by octave_run, octave_publish, octave_grabcode services.
"""

import os
import logging
from typing import Union, Literal, Tuple
from utils.config import get_env_str


logger = logging.getLogger(__name__)

# File size limits
MAX_TEXT_CHARS = 2000
MAX_BINARY_BYTES = 5 * 1024 * 1024  # 5MB

# Allowed directories from config
_allowed_dirs = [
    get_env_str("MCP_RUNS_ROOT", "/Users/hakankilicaslan/Git/octave-mcp/runs"),
    get_env_str("TMPDIR", "/Users/hakankilicaslan/Git/octave-mcp/runs"),
]
ALLOWED_DIRS = [d for d in _allowed_dirs if d is not None]


def _format_mcp_error(identifier: str, message: str, stack: str, ipucu: str) -> str:
    """Format error in MCP-compatible block format."""
    return f"""---MCP_ERROR_START---
identifier: {identifier}
message: {message}
stack: {stack}
ipucu: {ipucu}
---MCP_ERROR_END---"""


def __format_mcp_error(identifier: str, message: str, stack: str, ipucu: str) -> str:
    """Format error in MCP-compatible block format."""
    return f"""---MCP_ERROR_START---
identifier: {identifier}
message: {message}
stack: {stack}
ipucu: {ipucu}
---MCP_ERROR_END---"""


def _resolve_and_validate_path(file_path: str) -> Tuple[bool, str, str]:
    """
    Resolve symlinks and validate path is within allowed directories.

    Returns:
        (is_valid, resolved_path, error_message)
    """
    try:
        # Convert to absolute path and resolve symlinks
        resolved_path = os.path.realpath(os.path.abspath(file_path))

        # Check if resolved path is within any allowed directory
        for allowed_dir in ALLOWED_DIRS:
            allowed_abs = os.path.realpath(os.path.abspath(allowed_dir))
            if resolved_path.startswith(allowed_abs + os.sep) or resolved_path == allowed_abs:
                logger.info(f"Path access granted: {file_path} -> {resolved_path}")
                return True, resolved_path, ""

        # Path is outside whitelist
        error_msg = f"Access denied: path outside allowed directories {ALLOWED_DIRS}"
        logger.warning(f"Security violation: {file_path} -> {resolved_path} | {error_msg}")
        return False, resolved_path, error_msg

    except Exception as e:
        error_msg = f"Path resolution failed: {str(e)}"
        logger.error(f"Path validation error for {file_path}: {error_msg}")
        return False, file_path, error_msg


def read_file(file_path: str, mode: Literal["text", "binary"] = "text") -> Union[str, bytes]:
    """
    Safely read a file with whitelist and symlink validation.

    Args:
        file_path: Path to file to read
        mode: "text" for UTF-8 string, "binary" for bytes

    Returns:
        File content as str (text mode) or bytes (binary mode)

    Raises:
        PermissionError: Path outside allowed directories
        FileNotFoundError: File does not exist
        IOError: File read failed
    """
    # Validate path
    is_valid, resolved_path, error_msg = _resolve_and_validate_path(file_path)
    if not is_valid:
        raise PermissionError(
            _format_mcp_error(
                identifier="FILE_ACCESS_DENIED",
                message=error_msg,
                stack=f"read_file({file_path})",
                ipucu="Yalnızca MCP_RUNS_ROOT ve TMPDIR dizinlerine erişim izni vardır",
            )
        )

    # Check file exists
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(
            _format_mcp_error(
                identifier="FILE_NOT_FOUND",
                message=f"File not found: {resolved_path}",
                stack=f"read_file({file_path})",
                ipucu="Dosya yolu ve varlığını kontrol edin",
            )
        )

    # Read file
    try:
        if mode == "text":
            with open(resolved_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"Text file read successfully: {resolved_path} ({len(content)} chars)")
            return content
        else:  # binary
            with open(resolved_path, "rb") as f:
                content = f.read()
            logger.info(f"Binary file read successfully: {resolved_path} ({len(content)} bytes)")
            return content

    except Exception as e:
        error_msg = f"File read failed: {str(e)}"
        logger.error(f"IO error reading {resolved_path}: {error_msg}")
        raise IOError(
            _format_mcp_error(
                identifier="FILE_READ_ERROR",
                message=error_msg,
                stack=f"read_file({file_path})",
                ipucu="Dosya izinlerini ve disk alanını kontrol edin",
            )
        )


def write_file(
    file_path: str,
    content: Union[str, bytes],
    mode: Literal["text", "binary"] = "text",
    overwrite: bool = False,
) -> int:
    """
    Safely write a file with whitelist, size limits, and collision detection.

    Args:
        file_path: Path to file to write
        content: Content to write (str for text, bytes for binary)
        mode: "text" for UTF-8 string, "binary" for bytes
        overwrite: Allow overwriting existing files

    Returns:
        Number of characters (text) or bytes (binary) written

    Raises:
        PermissionError: Path outside allowed directories or file exists (overwrite=False)
        ValueError: Content too large or wrong type for mode
        IOError: File write failed
    """
    # Validate path
    is_valid, resolved_path, error_msg = _resolve_and_validate_path(file_path)
    if not is_valid:
        raise PermissionError(
            _format_mcp_error(
                identifier="FILE_ACCESS_DENIED",
                message=error_msg,
                stack=f"write_file({file_path})",
                ipucu="Yalnızca MCP_RUNS_ROOT ve TMPDIR dizinlerine erişim izni vardır",
            )
        )

    # Check overwrite policy
    if os.path.exists(resolved_path) and not overwrite:
        raise PermissionError(
            _format_mcp_error(
                identifier="FILE_EXISTS",
                message=f"File exists and overwrite=False: {resolved_path}",
                stack=f"write_file({file_path})",
                ipucu="overwrite=True kullanın veya farklı dosya adı seçin",
            )
        )

    # Validate content type and size
    if mode == "text":
        if not isinstance(content, str):
            raise ValueError(
                _format_mcp_error(
                    identifier="CONTENT_TYPE_MISMATCH",
                    message=f"Expected str for text mode, got {type(content).__name__}",
                    stack=f"write_file({file_path})",
                    ipucu="Text modu için string içerik kullanın",
                )
            )
        if len(content) > MAX_TEXT_CHARS:
            raise ValueError(
                _format_mcp_error(
                    identifier="FILE_SIZE_EXCEEDED",
                    message=f"Text content too large: {len(content)} > {MAX_TEXT_CHARS} chars",
                    stack=f"write_file({file_path})",
                    ipucu=f"Metin içeriği {MAX_TEXT_CHARS} karakterden az olmalı",
                )
            )
    else:  # binary
        if not isinstance(content, bytes):
            raise ValueError(
                _format_mcp_error(
                    identifier="CONTENT_TYPE_MISMATCH",
                    message=f"Expected bytes for binary mode, got {type(content).__name__}",
                    stack=f"write_file({file_path})",
                    ipucu="Binary modu için bytes içerik kullanın",
                )
            )
        if len(content) > MAX_BINARY_BYTES:
            raise ValueError(
                _format_mcp_error(
                    identifier="FILE_SIZE_EXCEEDED",
                    message=f"Binary content too large: {len(content)} > {MAX_BINARY_BYTES} bytes",
                    stack=f"write_file({file_path})",
                    ipucu=f"Binary içerik {MAX_BINARY_BYTES // (1024*1024)}MB'dan az olmalı",
                )
            )

    # Create directory if needed
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

    # Write file atomically (tmp file + rename)
    tmp_path = resolved_path + ".tmp"
    try:
        if mode == "text":
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)  # type: ignore  # content is str in text mode
        else:  # binary
            with open(tmp_path, "wb") as f:
                f.write(content)  # type: ignore  # content is bytes in binary mode

        # Atomic rename
        os.rename(tmp_path, resolved_path)

        size = len(content)
        logger.info(f"File written successfully: {resolved_path} ({size} {mode} units)")
        return size

    except Exception as e:
        # Clean up tmp file
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        error_msg = f"File write failed: {str(e)}"
        logger.error(f"IO error writing {resolved_path}: {error_msg}")
        raise IOError(
            _format_mcp_error(
                identifier="FILE_WRITE_ERROR",
                message=error_msg,
                stack=f"write_file({file_path})",
                ipucu="Disk alanı ve yazma izinlerini kontrol edin",
            )
        )


def get_allowed_directories() -> list[str]:
    """Return list of allowed directories for file operations."""
    return ALLOWED_DIRS.copy()
