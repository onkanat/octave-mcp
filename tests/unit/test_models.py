"""
Unit tests for Pydantic models.
"""

import pytest
from pathlib import Path
from pydantic import ValidationError

from src.models.requests import RunRequest, PublishRequest, CleanupRequest
from src.models.responses import RunResponse, PublishResponse, ImageResult, VectorizationWarning
from src.models.entities import Session, Run, ResourceLimits


class TestRunRequest:
    """Test RunRequest model validation."""

    def test_valid_run_request(self):
        """Test creating a valid run request."""
        request = RunRequest(code="x = 1 + 1; disp(x);", session_id="test_session_123")

        assert request.code == "x = 1 + 1; disp(x);"
        assert request.session_id == "test_session_123"

    def test_run_request_with_optional_fields(self):
        """Test run request with optional fields."""
        request = RunRequest(
            code="plot(1:10);", session_id="session_456", include_vectorization_warnings=True
        )

        assert request.include_vectorization_warnings is True

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

    def test_run_request_serialization(self):
        """Test run request serialization to dict."""
        request = RunRequest(code="x = 1;", session_id="test")
        data = request.model_dump()

        assert data["code"] == "x = 1;"
        assert data["session_id"] == "test"
        assert isinstance(data, dict)


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

    def test_run_response_with_images(self):
        """Test run response with image results."""
        image = ImageResult(
            name="plot.png",
            mime="image/png",
            size=1024,
            b64=(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42m"
                "P8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            ),
        )

        response = RunResponse(
            success=True,
            stdout="Plot generated",
            stderr="",
            exit_code=0,
            runtime_seconds=1.2,
            images=[image],
        )

        assert len(response.images) == 1
        assert response.images[0].name == "plot.png"
        assert response.images[0].size == 1024

    def test_run_response_with_vectorization_warnings(self):
        """Test run response with vectorization warnings."""
        warning = VectorizationWarning(
            lineno=5, col=10, message="Loop detected, consider vectorization"
        )

        response = RunResponse(
            success=True,
            stdout="Code executed",
            stderr="",
            exit_code=0,
            runtime_seconds=0.8,
            vectorization_warnings=[warning],
        )

        assert len(response.vectorization_warnings) == 1
        assert response.vectorization_warnings[0].lineno == 5
        assert "vectorization" in response.vectorization_warnings[0].message

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


class TestImageResult:
    """Test ImageResult model validation."""

    def test_valid_image_result(self):
        """Test creating a valid image result."""
        image = ImageResult(
            name="test_plot.png",
            mime="image/png",
            size=2048,
            b64=(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42m"
                "P8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            ),
        )

        assert image.name == "test_plot.png"
        assert image.mime == "image/png"
        assert image.size == 2048

    def test_image_result_without_b64(self):
        """Test image result without base64 data (vision mode)."""
        image = ImageResult(name="vision_plot.png", size=1536, path="/tmp/vision_plot.png")

        assert image.name == "vision_plot.png"
        assert image.b64 is None
        assert image.path == "/tmp/vision_plot.png"

    def test_negative_image_size_validation(self):
        """Test that negative image size raises validation error."""
        with pytest.raises(ValidationError):
            ImageResult(name="test.png", size=-100)


class TestVectorizationWarning:
    """Test VectorizationWarning model validation."""

    def test_valid_vectorization_warning(self):
        """Test creating a valid vectorization warning."""
        warning = VectorizationWarning(
            lineno=10, col=5, message="For loop detected, consider using vectorized operations"
        )

        assert warning.lineno == 10
        assert warning.col == 5
        assert "vectorized" in warning.message

    def test_negative_line_number_validation(self):
        """Test that negative line number raises validation error."""
        with pytest.raises(ValidationError):
            VectorizationWarning(lineno=0, col=5, message="test")  # Line numbers should start at 1

    def test_negative_column_validation(self):
        """Test that negative column raises validation error."""
        with pytest.raises(ValidationError):
            VectorizationWarning(lineno=1, col=-1, message="test")


class TestSession:
    """Test Session entity model."""

    def test_valid_session(self):
        """Test creating a valid session."""
        from pathlib import Path

        session = Session(
            session_id="session_123",
            work_dir=Path("/tmp/session_123"),
            created_at=1234567890.0,
            last_accessed=1234567890.0,
            description="Test session",
            session_dir="/tmp/session_123",
        )

        assert session.session_id == "session_123"
        assert str(session.work_dir) == "/tmp/session_123"


class TestRun:
    """Test Run entity model."""

    def test_valid_run(self):
        """Test creating a valid run."""
        limits = ResourceLimits()  # Use defaults

        run = Run(
            run_id="run_789",
            session_id="session_456",
            code="y = 2 * 3;",
            stdout="6",
            stderr="",
            exit_code=0,
            runtime_seconds=0.05,
            resource_limits=limits,
        )

        assert run.run_id == "run_789"
        assert run.code == "y = 2 * 3;"
        assert run.success is True  # Property based on exit_code
        assert run.runtime_seconds == 0.05

    def test_failed_run(self):
        """Test creating a failed run."""
        limits = ResourceLimits()  # Use defaults

        run = Run(
            run_id="run_fail",
            session_id="session_fail",
            code="invalid syntax",
            stdout="",
            stderr="error: syntax error",
            exit_code=1,
            runtime_seconds=0.02,
            resource_limits=limits,
        )

        assert run.success is False  # Property based on exit_code
        assert run.exit_code == 1
        assert "error" in run.stderr


class TestResourceLimits:
    """Test ResourceLimits model."""

    def test_valid_resource_limits(self):
        """Test creating valid resource limits."""
        limits = ResourceLimits(cpu_time_limit=30, memory_limit_mb=512, timeout=60)

        assert limits.cpu_time_limit == 30
        assert limits.memory_limit_mb == 512
        assert limits.timeout == 60

    def test_resource_limits_defaults(self):
        """Test resource limits with default values."""
        limits = ResourceLimits()

        assert limits.timeout == 60  # Default
        assert limits.max_output_chars == 20000  # Default
        assert limits.max_image_size_bytes == 5 * 1024 * 1024  # Default

    def test_resource_limits_validation(self):
        """Test resource limits validation."""
        # Test negative timeout should raise validation error
        with pytest.raises(ValidationError):
            ResourceLimits(timeout=-1)


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
