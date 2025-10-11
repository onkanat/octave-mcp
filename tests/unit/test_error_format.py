"""
Unit tests for error formatting utilities.
"""

import pytest
from src.utils.error_format import build_error_block, ErrorFormatter


class TestBuildErrorBlock:
    """Test build_error_block function."""

    def test_build_error_block_minimal(self):
        """Test error block with minimal parameters."""
        error_block = build_error_block(type="VALIDATION_ERROR", message="Invalid input")

        assert error_block["type"] == "VALIDATION_ERROR"
        assert error_block["message"] == "Invalid input"
        assert "id" in error_block
        assert "timestamp" in error_block
        assert error_block["details"] == {}

    def test_build_error_block_with_details(self):
        """Test error block with all parameters."""
        details = {"field": "username", "value": "invalid"}
        resource_violation = {"memory": "512MB", "limit": "256MB"}

        error_block = build_error_block(
            type="RESOURCE_ERROR",
            message="Memory limit exceeded",
            hint="Reduce data size",
            session_id="session_123",
            run_id="run_456",
            stdout_truncated=True,
            stderr_truncated=False,
            resource_violation=resource_violation,
            details=details,
        )

        assert error_block["type"] == "RESOURCE_ERROR"
        assert error_block["message"] == "Memory limit exceeded"
        assert error_block["hint"] == "Reduce data size"
        assert error_block["session_id"] == "session_123"
        assert error_block["run_id"] == "run_456"
        assert error_block["stdout_truncated"] is True
        assert error_block["stderr_truncated"] is False
        assert error_block["resource_violation"] == resource_violation
        assert error_block["details"] == details

    def test_build_error_block_unique_ids(self):
        """Test that each error block gets a unique ID."""
        error1 = build_error_block(type="ERROR", message="Test 1")
        error2 = build_error_block(type="ERROR", message="Test 2")

        assert error1["id"] != error2["id"]

    def test_build_error_block_timestamp_format(self):
        """Test timestamp format."""
        error_block = build_error_block(type="ERROR", message="Test")

        # Should be in ISO format
        timestamp = error_block["timestamp"]
        assert "T" in timestamp
        assert timestamp.endswith("Z")


class TestErrorFormatter:
    """Test ErrorFormatter class."""

    def test_format_error(self):
        """Test error formatting."""
        formatted = ErrorFormatter.format_error(
            identifier="ERR001",
            message="Test error",
            stack="line 1\nline 2",
            hint="Check your code",
        )

        assert formatted["identifier"] == "ERR001"
        assert formatted["message"] == "Test error"
        assert formatted["stack"] == "line 1\nline 2"
        assert formatted["hint"] == "Check your code"

    def test_format_error_empty_values(self):
        """Test error formatting with empty values."""
        formatted = ErrorFormatter.format_error(identifier="", message="", stack="", hint="")

        assert formatted["identifier"] == ""
        assert formatted["message"] == ""
        assert formatted["stack"] == ""
        assert formatted["hint"] == ""


@pytest.mark.integration
class TestErrorFormatIntegration:
    """Integration tests for error formatting."""

    def test_error_block_serialization(self):
        """Test that error blocks can be serialized."""
        import json

        error_block = build_error_block(
            type="TEST_ERROR", message="Test message", details={"key": "value"}
        )

        # Should be JSON serializable
        json_str = json.dumps(error_block)
        parsed = json.loads(json_str)

        assert parsed["type"] == "TEST_ERROR"
        assert parsed["message"] == "Test message"
        assert parsed["details"]["key"] == "value"

    def test_multiple_error_blocks(self):
        """Test creating multiple error blocks."""
        errors = []

        for i in range(3):
            error_block = build_error_block(
                type=f"ERROR_{i}", message=f"Error message {i}", session_id="test_session"
            )
            errors.append(error_block)

        # All should have different IDs but same session
        ids = [error["id"] for error in errors]
        assert len(set(ids)) == 3  # All unique

        for error in errors:
            assert error["session_id"] == "test_session"
