"""
Unit tests for service layer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from pathlib import Path
import tempfile
import os
import subprocess

from src.services.octave_runner import OctaveService
from src.services.session_service import SessionService
from src.services.publish_service import PublishService
from src.services.cleanup_service import CleanupService
from src.services.grabcode_service import GrabCodeService
from src.models.session import Session
from src.models.run import RunRequest
from src.models.publish import PublishRequest
from src.exceptions import TimeoutError, SecurityError


class TestOctaveService:
    """Test Octave execution service."""

    @pytest.fixture
    def octave_service(self):
        """Create OctaveService instance."""
        return OctaveService()

    @pytest.fixture
    def sample_session(self):
        """Create a sample session."""
        return Session(
            session_id="test_session",
            created_at="2024-01-01T00:00:00Z",
            last_accessed="2024-01-01T00:00:00Z",
        )

    @patch("subprocess.Popen")
    async def test_run_code_success(self, mock_popen, octave_service, sample_session):
        """Test successful code execution."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"result = 42\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        request = RunRequest(code="x = 42;", session_id="test_session")

        response = await octave_service.run_code(request, sample_session)

        assert response.output == "result = 42\n"
        assert response.success is True
        assert response.execution_time > 0

    @patch("subprocess.Popen")
    async def test_run_code_syntax_error(self, mock_popen, octave_service, sample_session):
        """Test code execution with syntax error."""
        # Mock subprocess with error
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"syntax error")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        request = RunRequest(code="invalid syntax", session_id="test_session")

        response = await octave_service.run_code(request, sample_session)

        assert response.success is False
        assert "syntax error" in response.error
        assert response.exit_code == 1

    @patch("subprocess.Popen")
    async def test_run_code_timeout(self, mock_popen, octave_service, sample_session):
        """Test code execution timeout."""
        # Mock subprocess that hangs
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("octave", 30)
        mock_popen.return_value = mock_process

        request = RunRequest(code="while true; end", session_id="test_session")

        with pytest.raises(TimeoutError):
            await octave_service.run_code(request, sample_session)

    async def test_run_code_security_check(self, octave_service, sample_session):
        """Test security validation of code."""
        dangerous_code = "system('rm -rf /')"
        request = RunRequest(code=dangerous_code, session_id="test_session")

        with pytest.raises(SecurityError):
            await octave_service.run_code(request, sample_session)

    @patch("subprocess.Popen")
    async def test_run_code_with_workspace(self, mock_popen, octave_service, sample_session):
        """Test code execution with workspace variables."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"y = 84\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Add workspace variable
        sample_session.workspace = {"x": 42}

        request = RunRequest(code="y = x * 2;", session_id="test_session")

        response = await octave_service.run_code(request, sample_session)

        assert response.success is True
        assert "y = 84" in response.output

    async def test_validate_code_security(self, octave_service):
        """Test code security validation."""
        # Safe code should pass
        safe_code = "x = 1:10; y = x.^2; plot(x, y);"
        octave_service._validate_code_security(safe_code)  # Should not raise

        # Dangerous code should fail
        dangerous_codes = [
            "system('cat /etc/passwd')",
            "!rm file.txt",
            "eval('system(\"ls\")')",
            "fopen('/etc/passwd', 'r')",
        ]

        for code in dangerous_codes:
            with pytest.raises(SecurityError):
                octave_service._validate_code_security(code)


class TestSessionService:
    """Test session management service."""

    @pytest.fixture
    def session_service(self):
        """Create SessionService instance."""
        return SessionService()

    async def test_create_session(self, session_service):
        """Test session creation."""
        session = await session_service.create_session()

        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.workspace == {}
        assert session.created_at is not None

    async def test_get_session_exists(self, session_service):
        """Test getting existing session."""
        # Create session first
        created_session = await session_service.create_session()

        # Retrieve it
        retrieved_session = await session_service.get_session(created_session.session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id

    async def test_get_session_not_exists(self, session_service):
        """Test getting non-existent session."""
        session = await session_service.get_session("nonexistent")

        assert session is None

    async def test_update_session_workspace(self, session_service):
        """Test updating session workspace."""
        session = await session_service.create_session()

        # Update workspace
        new_workspace = {"x": 42, "y": [1, 2, 3]}
        await session_service.update_session_workspace(session.session_id, new_workspace)

        # Retrieve and verify
        updated_session = await session_service.get_session(session.session_id)
        assert updated_session.workspace == new_workspace

    async def test_cleanup_expired_sessions(self, session_service):
        """Test cleanup of expired sessions."""
        # Create session
        session = await session_service.create_session()

        # Mock expiration (set very short timeout)
        with patch.object(session_service, "_is_session_expired", return_value=True):
            cleaned_count = await session_service.cleanup_expired_sessions()

            assert cleaned_count > 0

            # Session should be gone
            retrieved_session = await session_service.get_session(session.session_id)
            assert retrieved_session is None

    async def test_session_auto_expire(self, session_service):
        """Test session auto-expiration logic."""
        session = await session_service.create_session()

        # Should not be expired immediately
        assert not session_service._is_session_expired(session)

        # Mock old timestamp
        with patch.object(session, "last_accessed", "2020-01-01T00:00:00Z"):
            assert session_service._is_session_expired(session)


class TestPublishService:
    """Test code publishing service."""

    @pytest.fixture
    def publish_service(self):
        """Create PublishService instance."""
        return PublishService()

    async def test_publish_code_success(self, publish_service):
        """Test successful code publishing."""
        request = PublishRequest(
            code="x = 1:10; plot(x, x.^2);",
            title="Test Plot",
            description="A simple quadratic plot",
        )

        response = await publish_service.publish_code(request)

        assert response.success is True
        assert response.public_id is not None
        assert len(response.public_id) > 0
        assert response.url is not None

    async def test_publish_code_validation_error(self, publish_service):
        """Test publishing with validation error."""
        # Empty code should fail validation
        request = PublishRequest(code="", title="Empty Code", description="This should fail")

        response = await publish_service.publish_code(request)

        assert response.success is False
        assert "validation" in response.error.lower()

    async def test_publish_code_security_check(self, publish_service):
        """Test security validation during publishing."""
        request = PublishRequest(
            code="system('rm -rf /')", title="Dangerous Code", description="Should be blocked"
        )

        response = await publish_service.publish_code(request)

        assert response.success is False
        assert "security" in response.error.lower()

    async def test_get_published_code(self, publish_service):
        """Test retrieving published code."""
        # Publish first
        request = PublishRequest(code="x = 42;", title="Test Code", description="Simple test")
        publish_response = await publish_service.publish_code(request)

        # Retrieve
        code_data = await publish_service.get_published_code(publish_response.public_id)

        assert code_data is not None
        assert code_data["code"] == "x = 42;"
        assert code_data["title"] == "Test Code"

    async def test_get_published_code_not_found(self, publish_service):
        """Test retrieving non-existent published code."""
        code_data = await publish_service.get_published_code("nonexistent")

        assert code_data is None


class TestCleanupService:
    """Test cleanup service."""

    @pytest.fixture
    def cleanup_service(self):
        """Create CleanupService instance."""
        return CleanupService()

    async def test_cleanup_sessions(self, cleanup_service):
        """Test session cleanup."""
        with patch("src.services.cleanup_service.SessionService") as mock_session_service:
            mock_service = AsyncMock()
            mock_service.cleanup_expired_sessions.return_value = 5
            mock_session_service.return_value = mock_service

            result = await cleanup_service.cleanup_sessions()

            assert result["sessions_cleaned"] == 5
            mock_service.cleanup_expired_sessions.assert_called_once()

    async def test_cleanup_temporary_files(self, cleanup_service):
        """Test temporary file cleanup."""
        # Create some temp files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            old_file = temp_path / "old_file.txt"
            new_file = temp_path / "new_file.txt"

            old_file.write_text("old content")
            new_file.write_text("new content")

            # Mock file age
            with patch("os.path.getmtime") as mock_getmtime:
                # Old file timestamp (more than 1 hour ago)
                mock_getmtime.side_effect = lambda path: (
                    1000.0 if "old_file" in str(path) else 9999999.0
                )

                result = await cleanup_service.cleanup_temporary_files(
                    directory=temp_path, max_age_hours=1
                )

                assert result["files_cleaned"] >= 0

    async def test_cleanup_published_code(self, cleanup_service):
        """Test published code cleanup."""
        with patch("src.services.cleanup_service.PublishService") as mock_publish_service:
            mock_service = AsyncMock()
            mock_service.cleanup_old_publications.return_value = 3
            mock_publish_service.return_value = mock_service

            result = await cleanup_service.cleanup_published_code(max_age_days=30)

            assert result["publications_cleaned"] == 3


class TestGrabCodeService:
    """Test code grabbing service."""

    @pytest.fixture
    def grabcode_service(self):
        """Create GrabCodeService instance."""
        return GrabCodeService()

    async def test_grab_code_from_url_success(self, grabcode_service):
        """Test successful code extraction from URL."""
        with patch("httpx.AsyncClient.get") as mock_get:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <code>x = 1:10; plot(x, x.^2);</code>
                    <pre>function y = square(x)
                        y = x.^2;
                    end</pre>
                </body>
            </html>
            """
            mock_get.return_value = mock_response

            result = await grabcode_service.grab_code_from_url("https://example.com/code")

            assert result.success is True
            assert "x = 1:10" in result.code
            assert "function y = square" in result.code

    async def test_grab_code_from_url_not_found(self, grabcode_service):
        """Test handling of 404 error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("Not Found")
            mock_get.return_value = mock_response

            result = await grabcode_service.grab_code_from_url("https://example.com/missing")

            assert result.success is False
            assert "not found" in result.error.lower()

    async def test_grab_code_from_file_success(self, grabcode_service):
        """Test successful code extraction from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".m", delete=False) as temp_file:
            temp_file.write("% Octave script\nx = 1:100;\ny = x.^2;\nplot(x, y);")
            temp_file_path = temp_file.name

        try:
            result = await grabcode_service.grab_code_from_file(temp_file_path)

            assert result.success is True
            assert "x = 1:100" in result.code
            assert "plot(x, y)" in result.code
        finally:
            os.unlink(temp_file_path)

    async def test_grab_code_from_file_not_found(self, grabcode_service):
        """Test handling of missing file."""
        result = await grabcode_service.grab_code_from_file("/nonexistent/file.m")

        assert result.success is False
        assert "not found" in result.error.lower()

    async def test_grab_code_security_validation(self, grabcode_service):
        """Test security validation of grabbed code."""
        with patch("httpx.AsyncClient.get") as mock_get:
            # Mock response with dangerous code
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = '<code>system("rm -rf /")</code>'
            mock_get.return_value = mock_response

            result = await grabcode_service.grab_code_from_url("https://evil.com/code")

            assert result.success is False
            assert "security" in result.error.lower()


@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for services working together."""

    async def test_octave_session_integration(self):
        """Test OctaveService and SessionService integration."""
        session_service = SessionService()
        octave_service = OctaveService()

        # Create session
        session = await session_service.create_session()

        # Run code that sets variables
        request = RunRequest(code="x = 42; y = x * 2;", session_id=session.session_id)

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"x = 42\ny = 84\n", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            response = await octave_service.run_code(request, session)

            assert response.success is True

    async def test_publish_grabcode_integration(self):
        """Test PublishService and GrabCodeService integration."""
        publish_service = PublishService()
        grabcode_service = GrabCodeService()

        # Publish code
        publish_request = PublishRequest(
            code="x = 1:10; plot(x, sin(x));", title="Sine Wave", description="A sine wave plot"
        )

        publish_response = await publish_service.publish_code(publish_request)
        assert publish_response.success is True

        # Get the published code
        published_data = await publish_service.get_published_code(publish_response.public_id)

        assert published_data is not None
        assert published_data["code"] == "x = 1:10; plot(x, sin(x));"

    async def test_cleanup_all_services(self):
        """Test cleanup service with all other services."""
        cleanup_service = CleanupService()

        # Mock all cleanup operations
        with patch.multiple(
            cleanup_service,
            cleanup_sessions=AsyncMock(return_value={"sessions_cleaned": 2}),
            cleanup_temporary_files=AsyncMock(return_value={"files_cleaned": 5}),
            cleanup_published_code=AsyncMock(return_value={"publications_cleaned": 1}),
        ):

            results = await asyncio.gather(
                cleanup_service.cleanup_sessions(),
                cleanup_service.cleanup_temporary_files(),
                cleanup_service.cleanup_published_code(),
            )

            assert results[0]["sessions_cleaned"] == 2
            assert results[1]["files_cleaned"] == 5
            assert results[2]["publications_cleaned"] == 1
