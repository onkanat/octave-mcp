"""
Simplified unit tests for Pydantic models.
"""

import pytest
from pathlib import Path
from pydantic import ValidationError

from src.models.requests import RunRequest, PublishRequest, CleanupRequest
from src.models.responses import RunResponse, PublishResponse


class TestRunRequest:
    """Test RunRequest model validation."""

    def test_valid_run_request(self):
        """Test creating a valid run request."""
        request = RunRequest(code="x = 1 + 1; disp(x);", session_id="test_session_123")

        assert request.code == "x = 1 + 1; disp(x);"
        assert request.session_id == "test_session_123"

    def test_empty_code_validation(self):
        """Test that empty code raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RunRequest(code="", session_id="test")

        assert "at least 1 character" in str(exc_info.value)

    def test_whitespace_only_code_validation(self):
        """Test that whitespace-only code raises validation error."""
        with pytest.raises(ValidationError):
            RunRequest(code="   \n\t  ", session_id="test")

    def test_empty_session_id_validation(self):
        """Test that empty session ID raises validation error."""
        with pytest.raises(ValidationError):
            RunRequest(code="x = 1;", session_id="")

    def test_long_session_id_validation(self):
        """Test that overly long session ID raises validation error."""
        long_session_id = "x" * 256  # Exceeds 255 character limit

        with pytest.raises(ValidationError):
            RunRequest(code="x = 1;", session_id=long_session_id)


class TestPublishRequest:
    """Test PublishRequest model validation."""

    def test_valid_publish_request(self):
        """Test creating a valid publish request."""
        request = PublishRequest(
            code="plot(1:10); print('plot.png', '-dpng');", session_id="publish_session"
        )

        assert "plot" in request.code
        assert request.session_id == "publish_session"

    def test_publish_request_empty_code(self):
        """Test that empty code in publish request raises validation error."""
        with pytest.raises(ValidationError):
            PublishRequest(code="", session_id="test")


class TestCleanupRequest:
    """Test CleanupRequest model validation."""

    def test_valid_cleanup_request(self):
        """Test creating a valid cleanup request."""
        request = CleanupRequest(session_id="cleanup_session")

        assert request.session_id == "cleanup_session"

    def test_cleanup_request_empty_session_id(self):
        """Test that empty session ID raises validation error."""
        with pytest.raises(ValidationError):
            CleanupRequest(session_id="")


class TestRunResponse:
    """Test RunResponse model validation."""

    def test_valid_run_response(self):
        """Test creating a valid run response."""
        response = RunResponse(
            success=True, stdout="Result: 2", stderr="", exit_code=0, runtime_seconds=0.5
        )

        assert response.success is True
        assert response.stdout == "Result: 2"
        assert response.exit_code == 0
        assert response.runtime_seconds == 0.5

    def test_negative_runtime_validation(self):
        """Test that negative runtime raises validation error."""
        with pytest.raises(ValidationError):
            RunResponse(success=True, stdout="test", stderr="", exit_code=0, runtime_seconds=-1.0)


class TestPublishResponse:
    """Test PublishResponse model validation."""

    def test_valid_publish_response(self):
        """Test creating a valid publish response."""
        response = PublishResponse(
            html_b64="PGh0bWw+SGVsbG8gV29ybGQ8L2h0bWw+",  # Base64 encoded HTML
            html_original_size=1024,
            publish_dir="/tmp/publish",
            html_name="output.html",
            images=["plot1.png", "plot2.png"],
        )

        assert response.html_b64.startswith("PGh0bWw+")
        assert response.html_original_size == 1024
        assert len(response.images) == 2

    def test_negative_html_size_validation(self):
        """Test that negative HTML size raises validation error."""
        with pytest.raises(ValidationError):
            PublishResponse(
                html_b64="test", html_original_size=-1, publish_dir="/tmp", html_name="test.html"
            )


@pytest.mark.integration
class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_request_response_cycle(self):
        """Test complete request-response model cycle."""
        # Create request
        request = RunRequest(code="result = 5 * 6; disp(result);", session_id="integration_test")

        # Simulate processing and create response
        response = RunResponse(
            success=True, stdout="30", stderr="", exit_code=0, runtime_seconds=0.1
        )

        # Verify the cycle
        assert request.code in "result = 5 * 6; disp(result);"
        assert response.stdout == "30"
        assert response.success is True

    def test_model_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized."""
        original_request = RunRequest(code="test_code = 42;", session_id="roundtrip_test")

        # Serialize to dict
        data = original_request.model_dump()

        # Deserialize back to model
        restored_request = RunRequest(**data)

        assert restored_request.code == original_request.code
        assert restored_request.session_id == original_request.session_id
