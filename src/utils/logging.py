"""
Modern structured logging utilities.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import get_settings


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }

    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        formatted = super().format(record)

        # Reset color at the end
        return f"{formatted}{self.RESET}"


def setup_logging(
    level: Optional[str] = None, structured: bool = False, log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Use JSON structured logging
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    settings = get_settings()

    # Determine log level
    if level is None:
        level = settings.log_level

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get root logger
    logger = logging.getLogger("octave_mcp")

    # Clear existing handlers
    logger.handlers.clear()

    # Set logger level
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if structured:
        console_formatter = StructuredFormatter()
    else:
        console_formatter = ColoredConsoleFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level)

        # Always use structured format for file logs
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, level: int = logging.DEBUG):
    """
    Decorator to log function calls with arguments and return values.

    Args:
        logger: Logger instance
        level: Log level

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log function entry
            args_str = ", ".join([repr(arg) for arg in args])
            kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))

            logger.log(
                level,
                f"Calling {func.__name__}({all_args})",
                extra={"function": func.__name__, "args": args, "kwargs": kwargs},
            )

            try:
                result = func(*args, **kwargs)

                # Log successful return
                logger.log(
                    level,
                    f"{func.__name__} returned successfully",
                    extra={"function": func.__name__, "result_type": type(result).__name__},
                )

                return result

            except Exception as e:
                # Log exception
                logger.error(
                    f"{func.__name__} raised {type(e).__name__}: {e}",
                    extra={"function": func.__name__, "exception_type": type(e).__name__},
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_execution_time(logger: logging.Logger, level: int = logging.INFO):
    """
    Decorator to log function execution time.

    Args:
        logger: Logger instance
        level: Log level

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                logger.log(
                    level,
                    f"{func.__name__} executed in {execution_time:.3f}s",
                    extra={"function": func.__name__, "execution_time": execution_time},
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {execution_time:.3f}s: {e}",
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "exception_type": type(e).__name__,
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


# Global logger setup
_global_logger = None


def get_global_logger() -> logging.Logger:
    """Get the global application logger."""
    global _global_logger

    if _global_logger is None:
        _global_logger = setup_logging()

    return _global_logger


# Initialize default logging
setup_logging()
