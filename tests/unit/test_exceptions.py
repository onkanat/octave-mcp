"""
Unit tests for custom exceptions.
"""

import pytest

from src.exceptions import (
    MCPException,
    ValidationError,
    SecurityError,
    ResourceError,
    ServiceError,
    ExecutionError,
    TimeoutError,
    NotFoundError,
)


class TestMCPException:
    """Test base MCPException class."""

    def test_mcp_exception_creation(self):
        """Test creating a basic MCP exception."""
        exc = MCPException("Test error", "TEST_ERROR")

        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_mcp_exception_with_details(self):
        """Test MCP exception with details."""
        details = {"key": "value", "number": 42}
        exc = MCPException("Test error", "TEST_ERROR", details)

        assert exc.details == details
        assert exc.details["key"] == "value"
        assert exc.details["number"] == 42

    def test_mcp_exception_inheritance(self):
        """Test that MCP exception properly inherits from Exception."""
        exc = MCPException("Test error", "TEST_ERROR")

        assert isinstance(exc, Exception)
        assert isinstance(exc, MCPException)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test creating a validation error."""
        exc = ValidationError("Invalid field", "field_name", {"value": "invalid"})

        assert exc.message == "Invalid field"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field == "field_name"
        assert exc.details["value"] == "invalid"

    def test_validation_error_minimal(self):
        """Test creating validation error with minimal params."""
        exc = ValidationError("Field is required")

        assert exc.message == "Field is required"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field is None
        assert exc.details == {}

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        exc = ValidationError("Test", "test")

        assert isinstance(exc, MCPException)
        assert isinstance(exc, ValidationError)

    def test_validation_error_str(self):
        """Test string representation of validation error."""
        exc = ValidationError("Field is required", "username")

        assert str(exc) == "Field is required"


class TestSecurityError:
    """Test SecurityError exception."""

    def test_security_error_creation(self):
        """Test creating a security error."""
        details = {"path": "../etc/passwd"}
        exc = SecurityError("Path traversal detected", "/path/to/file", details)

        assert exc.message == "Path traversal detected"
        assert exc.error_code == "SECURITY_ERROR"
        assert exc.path == "/path/to/file"
        assert exc.details["path"] == "../etc/passwd"

    def test_security_error_minimal(self):
        """Test creating security error with minimal params."""
        exc = SecurityError("Access denied")

        assert exc.message == "Access denied"
        assert exc.error_code == "SECURITY_ERROR"
        assert exc.path is None
        assert exc.details == {}

    def test_security_error_inheritance(self):
        """Test SecurityError inheritance."""
        exc = SecurityError("Test")

        assert isinstance(exc, MCPException)
        assert isinstance(exc, SecurityError)


class TestResourceError:
    """Test ResourceError exception."""

    def test_resource_error_creation(self):
        """Test creating a resource error."""
        details = {"usage": "512MB", "limit": "256MB"}
        exc = ResourceError("Memory limit exceeded", "memory", details)

        assert exc.message == "Memory limit exceeded"
        assert exc.error_code == "RESOURCE_ERROR"
        assert exc.resource_type == "memory"
        assert exc.details["usage"] == "512MB"
        assert exc.details["limit"] == "256MB"

    def test_resource_error_minimal(self):
        """Test creating resource error with minimal params."""
        exc = ResourceError("Resource exhausted", "cpu")

        assert exc.message == "Resource exhausted"
        assert exc.error_code == "RESOURCE_ERROR"
        assert exc.resource_type == "cpu"
        assert exc.details == {}

    def test_resource_error_inheritance(self):
        """Test ResourceError inheritance."""
        exc = ResourceError("Test", "test")

        assert isinstance(exc, MCPException)
        assert isinstance(exc, ResourceError)


class TestServiceError:
    """Test ServiceError exception."""

    def test_service_error_creation(self):
        """Test creating a service error."""
        exc = ServiceError("Service unavailable", "octave", {"retry_count": 3})

        assert exc.message == "Service unavailable"
        assert exc.error_code == "SERVICE_ERROR"
        assert exc.service == "octave"
        assert exc.details["retry_count"] == 3

    def test_service_error_minimal(self):
        """Test creating service error with minimal params."""
        exc = ServiceError("Connection failed", "database")

        assert exc.message == "Connection failed"
        assert exc.error_code == "SERVICE_ERROR"
        assert exc.service == "database"
        assert exc.details == {}

    def test_service_error_inheritance(self):
        """Test ServiceError inheritance."""
        exc = ServiceError("Test", "test")

        assert isinstance(exc, MCPException)
        assert isinstance(exc, ServiceError)


class TestExecutionError:
    """Test ExecutionError exception."""

    def test_execution_error_creation(self):
        """Test creating an execution error."""
        details = {"command": "octave --eval 'error()'"}
        exc = ExecutionError("Code execution failed", 1, "output", "error msg", details)

        assert exc.message == "Code execution failed"
        assert exc.error_code == "EXECUTION_ERROR"
        assert exc.exit_code == 1
        assert exc.stdout == "output"
        assert exc.stderr == "error msg"
        assert exc.details["command"] == "octave --eval 'error()'"

    def test_execution_error_minimal(self):
        """Test creating execution error with minimal params."""
        exc = ExecutionError("Script failed", 2)

        assert exc.message == "Script failed"
        assert exc.error_code == "EXECUTION_ERROR"
        assert exc.exit_code == 2
        assert exc.stdout == ""
        assert exc.stderr == ""
        assert exc.details == {}

    def test_execution_error_inheritance(self):
        """Test ExecutionError inheritance."""
        exc = ExecutionError("Test", 1)

        assert isinstance(exc, MCPException)
        assert isinstance(exc, ExecutionError)


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_creation(self):
        """Test creating a timeout error."""
        details = {"elapsed": 35}
        exc = TimeoutError("Operation timed out", 30, details)

        assert exc.message == "Operation timed out"
        assert exc.error_code == "TIMEOUT_ERROR"
        assert exc.timeout_seconds == 30
        assert exc.details["elapsed"] == 35

    def test_timeout_error_minimal(self):
        """Test creating timeout error with minimal params."""
        exc = TimeoutError("Network timeout", 15)

        assert exc.message == "Network timeout"
        assert exc.error_code == "TIMEOUT_ERROR"
        assert exc.timeout_seconds == 15
        assert exc.details == {}

    def test_timeout_error_inheritance(self):
        """Test TimeoutError inheritance."""
        exc = TimeoutError("Test", 10)

        assert isinstance(exc, MCPException)
        assert isinstance(exc, TimeoutError)


class TestNotFoundError:
    """Test NotFoundError exception."""

    def test_not_found_error_creation(self):
        """Test creating a not found error."""
        details = {"query": "username=test"}
        exc = NotFoundError("Session not found", "session", "missing_123", details)

        assert exc.message == "Session not found"
        assert exc.error_code == "NOT_FOUND_ERROR"
        assert exc.resource_type == "session"
        assert exc.resource_id == "missing_123"
        assert exc.details["query"] == "username=test"

    def test_not_found_error_minimal(self):
        """Test creating not found error with minimal params."""
        exc = NotFoundError("File not found", "file", "test.txt")

        assert exc.message == "File not found"
        assert exc.error_code == "NOT_FOUND_ERROR"
        assert exc.resource_type == "file"
        assert exc.resource_id == "test.txt"
        assert exc.details == {}

    def test_not_found_error_inheritance(self):
        """Test NotFoundError inheritance."""
        exc = NotFoundError("Test", "test", "test")

        assert isinstance(exc, MCPException)
        assert isinstance(exc, NotFoundError)


class TestExceptionChaining:
    """Test exception chaining and context."""

    def test_exception_with_cause(self):
        """Test exception chaining with cause."""
        try:
            # Simulate an original exception
            raise ValueError("Original error")
        except ValueError as e:
            # Chain with our custom exception
            details = {"original": str(e)}
            exc = ExecutionError("Execution failed", 1, details=details)

            assert exc.details["original"] == "Original error"
            assert exc.message == "Execution failed"

    def test_nested_exception_context(self):
        """Test nested exception context handling."""
        details = {
            "operation": "file_read",
            "filename": "nonexistent.txt",
            "error_type": "FileNotFoundError",
        }

        exc = NotFoundError("File not found", "file", "nonexistent.txt", details)

        assert exc.resource_type == "file"
        assert exc.resource_id == "nonexistent.txt"
        assert exc.details["operation"] == "file_read"
        assert exc.details["filename"] == "nonexistent.txt"


@pytest.mark.integration
class TestExceptionIntegration:
    """Integration tests for exception handling."""

    def test_exception_serialization(self):
        """Test that exceptions can be serialized for API responses."""
        exc = ValidationError("Required field missing", "email", {"field": "email"})

        # Test that we can extract data for API responses
        error_data = {"message": exc.message, "error_code": exc.error_code, "details": exc.details}

        assert error_data["message"] == "Required field missing"
        assert error_data["error_code"] == "VALIDATION_ERROR"
        assert error_data["details"]["field"] == "email"

    def test_exception_in_try_catch(self):
        """Test exception handling in try-catch blocks."""
        with pytest.raises(SecurityError) as exc_info:
            raise SecurityError("Unauthorized access", details={"user": "anonymous"})

        caught_exc = exc_info.value
        assert caught_exc.message == "Unauthorized access"
        assert caught_exc.error_code == "SECURITY_ERROR"
        assert caught_exc.details["user"] == "anonymous"

    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""
        exceptions = [
            ValidationError("Validation failed"),
            SecurityError("Access denied"),
            ResourceError("Resource exhausted", "memory"),
            ServiceError("Service failed", "octave"),
            ExecutionError("Execution failed", 1),
            TimeoutError("Timeout occurred", 30),
            NotFoundError("Not found", "resource", "123"),
        ]

        for exc in exceptions:
            assert isinstance(exc, MCPException)
            assert hasattr(exc, "message")
            assert hasattr(exc, "error_code")
            assert hasattr(exc, "details")
