"""
Unit tests for utility modules.
"""

import pytest
from unittest.mock import patch
import tempfile
import os
import logging

from src.utils.config import get_settings, Settings
from src.utils.error_format import format_error_response
from src.utils.logging import setup_logging, get_logger
from src.utils.resource_limits import enforce_resource_limits
from src.utils.vectorization import process_code_with_llm


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.max_sessions == 10
        assert settings.session_timeout == 3600
        assert settings.max_execution_time == 30
        assert settings.max_memory_mb == 256
        assert settings.octave_path == "octave"

    @patch.dict(
        os.environ,
        {
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "MAX_SESSIONS": "20",
            "SESSION_TIMEOUT": "7200",
            "MAX_EXECUTION_TIME": "60",
            "MAX_MEMORY_MB": "512",
            "OCTAVE_PATH": "/usr/bin/octave",
        },
    )
    def test_settings_from_environment(self):
        """Test settings loaded from environment variables."""
        settings = Settings()

        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        assert settings.max_sessions == 20
        assert settings.session_timeout == 7200
        assert settings.max_execution_time == 60
        assert settings.max_memory_mb == 512
        assert settings.octave_path == "/usr/bin/octave"

    def test_settings_validation(self):
        """Test settings validation."""
        # Test negative values
        with pytest.raises(ValueError):
            Settings(max_sessions=-1)

        with pytest.raises(ValueError):
            Settings(session_timeout=0)

        with pytest.raises(ValueError):
            Settings(max_execution_time=0)

        with pytest.raises(ValueError):
            Settings(max_memory_mb=0)

    def test_settings_immutable(self):
        """Test that settings are immutable after creation."""
        settings = Settings()

        # Should not be able to modify after creation
        with pytest.raises(AttributeError):
            settings.debug = True


class TestGetSettings:
    """Test the get_settings function."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_get_settings_with_env(self):
        """Test get_settings with environment variables."""
        # Clear any cached settings
        if hasattr(get_settings, "_cached_settings"):
            delattr(get_settings, "_cached_settings")

        settings = get_settings()
        assert settings.debug is True


class TestErrorFormat:
    """Test error formatting utilities."""

    def test_format_error_response_basic(self):
        """Test basic error response formatting."""
        error_response = format_error_response("Test error", "TEST_CODE")

        assert error_response["error"]["message"] == "Test error"
        assert error_response["error"]["code"] == "TEST_CODE"
        assert "timestamp" in error_response
        assert error_response["success"] is False

    def test_format_error_response_with_details(self):
        """Test error response formatting with details."""
        details = {"field": "username", "value": "invalid"}
        error_response = format_error_response("Validation failed", "VALIDATION_ERROR", details)

        assert error_response["error"]["details"] == details
        assert error_response["error"]["details"]["field"] == "username"

    def test_format_error_response_with_request_id(self):
        """Test error response formatting with request ID."""
        error_response = format_error_response("Test error", "TEST_CODE", request_id="req-123")

        assert error_response["request_id"] == "req-123"

    def test_format_error_response_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        error_response = format_error_response("Test error", "TEST_CODE")

        # Should be able to parse as ISO timestamp
        from datetime import datetime

        timestamp = datetime.fromisoformat(error_response["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)


class TestLogging:
    """Test logging utilities."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()

        assert logger.name == "octave_mcp"
        assert logger.level == 20  # INFO level

    def test_setup_logging_debug(self):
        """Test debug logging setup."""
        logger = setup_logging(level="DEBUG")

        assert logger.level == 10  # DEBUG level

    def test_setup_logging_file_output(self):
        """Test logging to file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_log:
            temp_log_path = temp_log.name

        try:
            logger = setup_logging(log_file=temp_log_path)
            logger.info("Test log message")

            # Check that log file was created and contains message
            with open(temp_log_path, "r") as f:
                content = f.read()
                assert "Test log message" in content
        finally:
            os.unlink(temp_log_path)

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_module")

        assert logger.name == "octave_mcp.test_module"
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_get_logger_child(self):
        """Test child logger creation."""
        child_logger = get_logger("parent.child")

        assert child_logger.name == "octave_mcp.parent.child"


class TestResourceLimits:
    """Test resource limit enforcement."""

    @patch("resource.setrlimit")
    @patch("resource.getrlimit")
    def test_enforce_resource_limits_success(self, mock_getrlimit, mock_setrlimit):
        """Test successful resource limit enforcement."""
        # Mock current limits
        mock_getrlimit.return_value = (1000, 2000)

        # Should not raise exception
        enforce_resource_limits(max_memory_mb=100, max_execution_time=30)

        # Verify setrlimit was called
        assert mock_setrlimit.called

    @patch("resource.setrlimit")
    def test_enforce_resource_limits_memory(self, mock_setrlimit):
        """Test memory limit enforcement."""
        enforce_resource_limits(max_memory_mb=256)

        # Check that setrlimit was called with memory limit
        calls = mock_setrlimit.call_args_list
        memory_calls = [call for call in calls if call[0][0] == 2]  # RLIMIT_AS = 2
        assert len(memory_calls) > 0

    @patch("resource.setrlimit")
    def test_enforce_resource_limits_time(self, mock_setrlimit):
        """Test execution time limit enforcement."""
        enforce_resource_limits(max_execution_time=60)

        # Check that setrlimit was called with time limit
        calls = mock_setrlimit.call_args_list
        time_calls = [call for call in calls if call[0][0] == 0]  # RLIMIT_CPU = 0
        assert len(time_calls) > 0

    @patch("resource.setrlimit", side_effect=OSError("Permission denied"))
    def test_enforce_resource_limits_permission_error(self, mock_setrlimit):
        """Test handling of permission errors."""
        # Should not raise exception, just log warning
        enforce_resource_limits(max_memory_mb=100)

    def test_enforce_resource_limits_invalid_params(self):
        """Test validation of resource limit parameters."""
        with pytest.raises(ValueError):
            enforce_resource_limits(max_memory_mb=-1)

        with pytest.raises(ValueError):
            enforce_resource_limits(max_execution_time=0)


class TestVectorization:
    """Test vectorization utilities."""

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_success(self, mock_post):
        """Test successful LLM processing."""
        # Mock successful API response
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Optimized vectorized code here"}}]
        }
        mock_response.raise_for_status.return_value = None

        result = await process_code_with_llm("x = 1:100; y = x.^2;")

        assert "Optimized vectorized code here" in result
        mock_post.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_api_error(self, mock_post):
        """Test LLM API error handling."""
        # Mock API error
        mock_response = mock_post.return_value
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on error
        assert result == "x = 1:100;"

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_timeout(self, mock_post):
        """Test LLM API timeout handling."""
        # Mock timeout
        mock_post.side_effect = Exception("Timeout")

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on timeout
        assert result == "x = 1:100;"

    async def test_process_code_with_llm_empty_code(self):
        """Test processing empty code."""
        result = await process_code_with_llm("")

        assert result == ""

    async def test_process_code_with_llm_none_code(self):
        """Test processing None code."""
        result = await process_code_with_llm(None)

        assert result is None

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_invalid_response(self, mock_post):
        """Test handling of invalid API response."""
        # Mock invalid response structure
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_response.raise_for_status.return_value = None

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on invalid response
        assert result == "x = 1:100;"


@pytest.mark.integration
class TestUtilsIntegration:
    """Integration tests for utility modules."""

    def test_settings_logging_integration(self):
        """Test integration between settings and logging."""
        settings = get_settings()
        logger = setup_logging(level=settings.log_level)

        assert logger.level == getattr(logging, settings.log_level)

    def test_error_format_logging_integration(self):
        """Test integration between error formatting and logging."""
        logger = get_logger("test")
        error_response = format_error_response("Test error", "TEST_CODE")

        # Should be able to log the error response
        logger.error("Error occurred: %s", error_response["error"]["message"])

        assert error_response["error"]["message"] == "Test error"

    @patch("resource.setrlimit")
    def test_settings_resource_limits_integration(self, mock_setrlimit):
        """Test integration between settings and resource limits."""
        settings = get_settings()

        enforce_resource_limits(
            max_memory_mb=settings.max_memory_mb, max_execution_time=settings.max_execution_time
        )

        assert mock_setrlimit.called
