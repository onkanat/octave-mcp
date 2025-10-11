"""
Unit tests for Pydantic model validation and constraints.
"""

import pytest
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from src.models.entities import Session, ResourceLimits, Run


class TestResourceLimitsModel:
    """Test ResourceLimits Pydantic model."""

    def test_resource_limits_defaults(self):
        """Test ResourceLimits with default values."""
        limits = ResourceLimits()

        assert limits.cpu_time_limit is None
        assert limits.memory_limit_mb is None
        assert limits.max_output_chars == 20000
        assert limits.max_image_size_bytes == 5 * 1024 * 1024
        assert limits.timeout == 60

    def test_resource_limits_custom_values(self):
        """Test ResourceLimits with custom values."""
        limits = ResourceLimits(
            cpu_time_limit=30,
            memory_limit_mb=512,
            max_output_chars=10000,
            max_image_size_bytes=1024 * 1024,
            timeout=120,
        )

        assert limits.cpu_time_limit == 30
        assert limits.memory_limit_mb == 512
        assert limits.max_output_chars == 10000
        assert limits.max_image_size_bytes == 1024 * 1024
        assert limits.timeout == 120

    def test_resource_limits_validation_zero_negative(self):
        """Test ResourceLimits validation rejects zero/negative values."""
        # Zero CPU time limit
        with pytest.raises(ValidationError) as exc_info:
            ResourceLimits(cpu_time_limit=0)
        assert "Resource limits must be positive" in str(exc_info.value)

        # Negative memory limit
        with pytest.raises(ValidationError) as exc_info:
            ResourceLimits(memory_limit_mb=-100)
        assert "Resource limits must be positive" in str(exc_info.value)

        # Zero timeout
        with pytest.raises(ValidationError) as exc_info:
            ResourceLimits(timeout=0)
        assert "Resource limits must be positive" in str(exc_info.value)


class TestRunModel:
    """Test Run Pydantic model."""

    def test_run_creation_minimal(self):
        """Test creating Run with minimal required fields."""
        resource_limits = ResourceLimits()

        run = Run(
            run_id="test_run",
            code="print('hello')",
            exit_code=0,
            runtime_seconds=1.5,
            resource_limits=resource_limits,
        )

        assert run.run_id == "test_run"
        assert run.session_id is None
        assert run.code == "print('hello')"
        assert run.stdout == ""  # Default
        assert run.stderr == ""  # Default
        assert run.exit_code == 0
        assert run.runtime_seconds == 1.5
        assert run.images == []  # Default
        assert isinstance(run.created_at, datetime)

    def test_run_creation_with_session(self):
        """Test creating Run with session ID."""
        resource_limits = ResourceLimits()

        run = Run(
            run_id="session_run",
            session_id="session_123",
            code="plot([1,2,3])",
            stdout="Output text",
            stderr="Warning message",
            exit_code=0,
            runtime_seconds=2.3,
            resource_limits=resource_limits,
            images=["image1.png", "image2.png"],
        )

        assert run.run_id == "session_run"
        assert run.session_id == "session_123"
        assert run.code == "plot([1,2,3])"
        assert run.stdout == "Output text"
        assert run.stderr == "Warning message"
        assert run.images == ["image1.png", "image2.png"]

    def test_run_validation_required_fields(self):
        """Test Run validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Run()  # Missing all required fields

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "run_id" in required_fields
        assert "code" in required_fields
        assert "exit_code" in required_fields
        assert "runtime_seconds" in required_fields
        assert "resource_limits" in required_fields

    def test_run_with_invalid_runtime(self):
        """Test Run validation with invalid runtime."""
        resource_limits = ResourceLimits()

        # Negative runtime should be rejected
        with pytest.raises(ValidationError) as exc_info:
            Run(
                run_id="negative_runtime",
                code="test",
                exit_code=0,
                runtime_seconds=-1.0,
                resource_limits=resource_limits,
            )
        assert "Runtime must be non-negative" in str(exc_info.value)

    def test_run_success_property(self):
        """Test the success property of Run."""
        resource_limits = ResourceLimits()

        # Successful run (exit_code = 0)
        successful_run = Run(
            run_id="success_test",
            code="test",
            exit_code=0,
            runtime_seconds=1.0,
            resource_limits=resource_limits,
        )
        assert successful_run.success is True

        # Failed run (exit_code != 0)
        failed_run = Run(
            run_id="fail_test",
            code="test",
            exit_code=1,
            runtime_seconds=1.0,
            resource_limits=resource_limits,
        )
        assert failed_run.success is False


class TestSessionModel:
    """Test Session Pydantic model."""

    def test_session_creation_minimal(self):
        """Test creating Session with minimal required fields."""
        session = Session(
            session_id="test_session",
            work_dir="/tmp/test",
            created_at=1234567890.0,
            last_accessed=1234567890.0,
        )

        assert session.session_id == "test_session"
        assert session.work_dir == Path("/tmp/test")
        assert session.persistent is False  # Default value
        assert session.run_count == 0  # Default value
        assert session.description is None
        assert session.session_dir is None

    def test_session_path_conversion(self):
        """Test work_dir path conversion."""
        # String path should be converted to Path
        session = Session(
            session_id="path_test",
            work_dir="/tmp/string_path",
            created_at=1234567890.0,
            last_accessed=1234567890.0,
        )
        assert isinstance(session.work_dir, Path)
        assert str(session.work_dir) == "/tmp/string_path"

    def test_session_update_activity(self):
        """Test updating session activity."""
        session = Session(
            session_id="activity_test",
            work_dir="/tmp/activity",
            created_at=1234567890.0,
            last_accessed=1234567890.0,
        )

        original_last_active = session.last_active
        session.update_activity()

        assert session.last_active > original_last_active


@pytest.mark.integration
class TestModelIntegration:
    """Test model integration and serialization."""

    def test_model_serialization(self):
        """Test model serialization to dict."""
        limits = ResourceLimits(cpu_time_limit=10)

        run = Run(
            run_id="serialize_test",
            code="test code",
            exit_code=0,
            runtime_seconds=1.0,
            resource_limits=limits,
        )

        # Convert to dict
        run_dict = run.model_dump()

        assert run_dict["run_id"] == "serialize_test"
        assert run_dict["code"] == "test code"
        assert "resource_limits" in run_dict
        assert run_dict["resource_limits"]["cpu_time_limit"] == 10

    def test_run_with_session_integration(self):
        """Test creating Run with session data."""
        session = Session(
            session_id="integration_session",
            work_dir="/tmp/integration",
            created_at=1234567890.0,
            last_accessed=1234567890.0,
        )

        limits = ResourceLimits(timeout=120)

        run = Run(
            run_id="integration_run",
            session_id=session.session_id,
            code="integration test",
            exit_code=0,
            runtime_seconds=45.0,
            resource_limits=limits,
        )

        assert run.session_id == session.session_id
        assert run.resource_limits.timeout == 120
