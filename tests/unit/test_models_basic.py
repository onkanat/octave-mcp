"""
Unit tests for simple model classes.
"""

import pytest
from datetime import datetime

from src.models.grabcode import Grabcode
from src.models.session import Session


class TestGrabcode:
    """Test Grabcode model class."""

    def test_grabcode_creation(self):
        """Test creating a Grabcode instance."""
        grabcode = Grabcode(
            code_b64="aGVsbG8gd29ybGQ=",  # "hello world" in base64
            line_count=5,
            warnings=["warning1", "warning2"],
        )

        assert grabcode.code_b64 == "aGVsbG8gd29ybGQ="
        assert grabcode.line_count == 5
        assert grabcode.warnings == ["warning1", "warning2"]

    def test_grabcode_no_warnings(self):
        """Test creating Grabcode with no warnings."""
        grabcode = Grabcode(code_b64="Y29kZQ==", line_count=1, warnings=None)  # "code" in base64

        assert grabcode.code_b64 == "Y29kZQ=="
        assert grabcode.line_count == 1
        assert grabcode.warnings == []  # Should default to empty list

    def test_grabcode_empty_warnings(self):
        """Test creating Grabcode with empty warnings list."""
        grabcode = Grabcode(code_b64="dGVzdA==", line_count=10, warnings=[])  # "test" in base64

        assert grabcode.warnings == []

    def test_grabcode_attributes_types(self):
        """Test that Grabcode attributes have correct types."""
        grabcode = Grabcode("abc123", 42, ["warn"])

        assert isinstance(grabcode.code_b64, str)
        assert isinstance(grabcode.line_count, int)
        assert isinstance(grabcode.warnings, list)

    def test_grabcode_modify_warnings(self):
        """Test modifying warnings after creation."""
        grabcode = Grabcode("code", 1, ["initial"])

        # Should be able to modify warnings
        grabcode.warnings.append("new_warning")
        assert "new_warning" in grabcode.warnings
        assert len(grabcode.warnings) == 2


class TestSession:
    """Test Session model class."""

    def test_session_creation(self):
        """Test creating a Session instance."""
        session = Session(session_id="test_session_123", persistent=True, work_dir="/tmp/test")

        assert session.session_id == "test_session_123"
        assert session.persistent is True
        assert session.work_dir == "/tmp/test"
        assert isinstance(session.start_time, datetime)
        assert isinstance(session.last_active, datetime)

    def test_session_non_persistent(self):
        """Test creating a non-persistent session."""
        session = Session(session_id="temp_session", persistent=False, work_dir="/tmp/temp")

        assert session.session_id == "temp_session"
        assert session.persistent is False
        assert session.work_dir == "/tmp/temp"

    def test_session_timestamps(self):
        """Test that session timestamps are set correctly."""
        session = Session("test", True, "/tmp")

        # Start time and last active should be close to now
        now = datetime.now()
        time_diff_start = abs((now - session.start_time).total_seconds())
        time_diff_active = abs((now - session.last_active).total_seconds())

        # Should be within 1 second
        assert time_diff_start < 1.0
        assert time_diff_active < 1.0

    def test_session_update_last_active(self):
        """Test updating last_active timestamp."""
        session = Session("test", True, "/tmp")
        original_last_active = session.last_active

        # Wait a tiny bit and update
        import time

        time.sleep(0.01)
        session.last_active = datetime.now()

        assert session.last_active > original_last_active

    def test_session_attributes_immutable(self):
        """Test that core session attributes can be modified."""
        session = Session("original", True, "/original")

        # Should be able to change attributes
        session.session_id = "modified"
        session.persistent = False
        session.work_dir = "/modified"

        assert session.session_id == "modified"
        assert session.persistent is False
        assert session.work_dir == "/modified"

    def test_session_string_representation(self):
        """Test string properties of session."""
        session = Session("test_123", True, "/path/to/work")

        # All string attributes should be strings
        assert isinstance(session.session_id, str)
        assert isinstance(session.work_dir, str)

        # Should be able to use in string contexts
        session_str = f"Session {session.session_id}"
        assert "test_123" in session_str


@pytest.mark.integration
class TestModelIntegration:
    """Integration tests for simple models."""

    def test_models_together(self):
        """Test using models together."""
        session = Session("integration_test", True, "/tmp/integration")
        grabcode = Grabcode("aW50ZWdyYXRpb24=", 3, ["integration warning"])

        # Should be able to associate them conceptually
        test_data = {"session": session, "code": grabcode}

        assert test_data["session"].session_id == "integration_test"
        assert test_data["code"].line_count == 3

    def test_model_serialization_concept(self):
        """Test that models can be converted to dictionaries."""
        session = Session("serialize_test", False, "/tmp/serialize")

        # Convert to dict-like structure
        session_dict = {
            "session_id": session.session_id,
            "persistent": session.persistent,
            "work_dir": session.work_dir,
            "start_time": session.start_time.isoformat(),
            "last_active": session.last_active.isoformat(),
        }

        assert session_dict["session_id"] == "serialize_test"
        assert session_dict["persistent"] is False
        assert "T" in session_dict["start_time"]  # ISO format

    def test_models_validation_concept(self):
        """Test basic validation concepts."""
        # Valid session
        valid_session = Session("valid_id", True, "/valid/path")
        assert len(valid_session.session_id) > 0
        assert valid_session.work_dir.startswith("/")

        # Valid grabcode
        valid_grabcode = Grabcode("dGVzdA==", 5, [])
        assert valid_grabcode.line_count > 0
        assert isinstance(valid_grabcode.warnings, list)
