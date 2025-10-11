"""
Unit tests for utility modules.
"""

import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os

from src.utils.error_format import format_error_response
from src.utils.logging import setup_logging, get_logger


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
        # Import here to avoid module-level import issues
        from src.utils.resource_limits import enforce_resource_limits

        # Mock current limits
        mock_getrlimit.return_value = (1000, 2000)

        # Should not raise exception
        enforce_resource_limits(max_memory_mb=100, max_execution_time=30)

        # Verify setrlimit was called
        assert mock_setrlimit.called

    @patch("resource.setrlimit")
    def test_enforce_resource_limits_memory(self, mock_setrlimit):
        """Test memory limit enforcement."""
        from src.utils.resource_limits import enforce_resource_limits

        enforce_resource_limits(max_memory_mb=256)

        # Check that setrlimit was called with memory limit
        calls = mock_setrlimit.call_args_list
        memory_calls = [call for call in calls if call[0][0] == 2]  # RLIMIT_AS = 2
        assert len(memory_calls) > 0

    @patch("resource.setrlimit")
    def test_enforce_resource_limits_time(self, mock_setrlimit):
        """Test execution time limit enforcement."""
        from src.utils.resource_limits import enforce_resource_limits

        enforce_resource_limits(max_execution_time=60)

        # Check that setrlimit was called with time limit
        calls = mock_setrlimit.call_args_list
        time_calls = [call for call in calls if call[0][0] == 0]  # RLIMIT_CPU = 0
        assert len(time_calls) > 0

    @patch("resource.setrlimit", side_effect=OSError("Permission denied"))
    def test_enforce_resource_limits_permission_error(self, mock_setrlimit):
        """Test handling of permission errors."""
        from src.utils.resource_limits import enforce_resource_limits

        # Should not raise exception, just log warning
        enforce_resource_limits(max_memory_mb=100)

    def test_enforce_resource_limits_invalid_params(self):
        """Test validation of resource limit parameters."""
        from src.utils.resource_limits import enforce_resource_limits

        with pytest.raises(ValueError):
            enforce_resource_limits(max_memory_mb=-1)

        with pytest.raises(ValueError):
            enforce_resource_limits(max_execution_time=0)


class TestVectorization:
    """Test vectorization utilities."""

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_success(self, mock_post):
        """Test successful LLM processing."""
        from src.utils.vectorization import process_code_with_llm

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Optimized vectorized code here"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = await process_code_with_llm("x = 1:100; y = x.^2;")

        assert "Optimized vectorized code here" in result
        mock_post.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_api_error(self, mock_post):
        """Test LLM API error handling."""
        from src.utils.vectorization import process_code_with_llm

        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on error
        assert result == "x = 1:100;"

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_timeout(self, mock_post):
        """Test LLM API timeout handling."""
        from src.utils.vectorization import process_code_with_llm

        # Mock timeout
        mock_post.side_effect = Exception("Timeout")

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on timeout
        assert result == "x = 1:100;"

    async def test_process_code_with_llm_empty_code(self):
        """Test processing empty code."""
        from src.utils.vectorization import process_code_with_llm

        result = await process_code_with_llm("")

        assert result == ""

    async def test_process_code_with_llm_none_code(self):
        """Test processing None code."""
        from src.utils.vectorization import process_code_with_llm

        result = await process_code_with_llm(None)

        assert result is None

    @patch("httpx.AsyncClient.post")
    async def test_process_code_with_llm_invalid_response(self, mock_post):
        """Test handling of invalid API response."""
        from src.utils.vectorization import process_code_with_llm

        # Mock invalid response structure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = await process_code_with_llm("x = 1:100;")

        # Should return original code on invalid response
        assert result == "x = 1:100;"


class TestSecurity:
    """Test security utilities."""

    def test_validate_code_path_traversal(self):
        """Test path traversal detection."""
        from src.utils.security import validate_code_security

        # Should detect path traversal attempts
        dangerous_codes = ["../etc/passwd", "../../secret.txt", "/etc/shadow", "~/.ssh/id_rsa"]

        for code in dangerous_codes:
            with pytest.raises(Exception):  # Should raise SecurityError
                validate_code_security(code)

    def test_validate_code_system_commands(self):
        """Test system command detection."""
        from src.utils.security import validate_code_security

        # Should detect system commands
        dangerous_codes = [
            "system('rm -rf /')",
            "!ls -la",
            "eval('system(cmd)')",
            "subprocess.run(['rm', 'file'])",
        ]

        for code in dangerous_codes:
            with pytest.raises(Exception):  # Should raise SecurityError
                validate_code_security(code)

    def test_validate_code_safe_octave(self):
        """Test that safe Octave code passes validation."""
        from src.utils.security import validate_code_security

        # Safe Octave code should pass
        safe_codes = [
            "x = 1:10; y = x.^2; plot(x, y);",
            "A = magic(5); det(A);",
            "function y = square(x); y = x.^2; end",
            "for i = 1:10; disp(i); end",
        ]

        for code in safe_codes:
            # Should not raise exception
            validate_code_security(code)


@pytest.mark.integration
class TestUtilsIntegration:
    """Integration tests for utility modules."""

    def test_error_format_logging_integration(self):
        """Test integration between error formatting and logging."""
        logger = get_logger("test")
        error_response = format_error_response("Test error", "TEST_CODE")

        # Should be able to log the error response
        logger.error("Error occurred: %s", error_response["error"]["message"])

        assert error_response["error"]["message"] == "Test error"

    @patch("resource.setrlimit")
    def test_resource_limits_integration(self, mock_setrlimit):
        """Test resource limits integration."""
        from src.utils.resource_limits import enforce_resource_limits

        enforce_resource_limits(max_memory_mb=256, max_execution_time=30)

        assert mock_setrlimit.called
