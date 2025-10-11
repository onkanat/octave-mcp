"""
Unit tests for utils.file_io module.

Tests cover:
- Path whitelist validation (allowed/denied directories)
- Symlink resolution and target validation
- File size limits (text 2000 chars, binary 5MB)
- Overwrite policies and collision detection
- MCP error block formatting
- Concurrent write scenarios
"""

import os
import tempfile
import pytest
import threading
from unittest.mock import patch
from utils.file_io import read_file, write_file, get_allowed_directories
from utils.file_io import MAX_TEXT_CHARS, MAX_BINARY_BYTES


class TestFileIOSecurity:
    """Test security and access control features."""

    def test_get_allowed_directories(self):
        """Test that allowed directories are correctly configured."""
        dirs = get_allowed_directories()
        assert isinstance(dirs, list)
        assert len(dirs) >= 1  # At least MCP_RUNS_ROOT should be configured

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_path_whitelist_allowed(self):
        """Test that files within allowed directories can be accessed."""
        # Create test file in allowed directory
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/test.txt"

        with open(test_file, "w") as f:
            f.write("test content")

        try:
            # Should succeed
            content = read_file(test_file, mode="text")
            assert content == "test content"
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_path_whitelist_denied(self):
        """Test that files outside allowed directories are blocked."""
        # Try to access file outside allowed directory
        with pytest.raises(PermissionError) as exc_info:
            read_file("/etc/passwd", mode="text")

        assert "FILE_ACCESS_DENIED" in str(exc_info.value)
        assert "outside allowed directories" in str(exc_info.value)

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_symlink_resolution_allowed_target(self):
        """Test symlink pointing to allowed directory is permitted."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)

        # Create target file in allowed directory
        target_file = "/tmp/test-allowed/target.txt"
        with open(target_file, "w") as f:
            f.write("symlink target")

        # Create symlink in allowed directory pointing to allowed target
        symlink_file = "/tmp/test-allowed/link.txt"
        os.symlink(target_file, symlink_file)

        try:
            # Should succeed - symlink target is in allowed directory
            content = read_file(symlink_file, mode="text")
            assert content == "symlink target"
        finally:
            # Cleanup
            for path in [symlink_file, target_file]:
                if os.path.exists(path):
                    os.unlink(path)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_symlink_resolution_denied_target(self):
        """Test symlink pointing outside allowed directory is blocked."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)

        # Create symlink in allowed directory pointing to forbidden target
        symlink_file = "/tmp/test-allowed/bad_link.txt"
        os.symlink("/etc/passwd", symlink_file)

        try:
            # Should fail - symlink target is outside allowed directory
            with pytest.raises(PermissionError) as exc_info:
                read_file(symlink_file, mode="text")

            assert "FILE_ACCESS_DENIED" in str(exc_info.value)
        finally:
            # Cleanup
            if os.path.exists(symlink_file):
                os.unlink(symlink_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")


class TestFileSizeLimits:
    """Test file size limit enforcement."""

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_text_size_limit_within_bounds(self):
        """Test text write within size limits succeeds."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/small_text.txt"

        # Content within limit (2000 chars)
        content = "x" * (MAX_TEXT_CHARS - 100)

        try:
            bytes_written = write_file(test_file, content, mode="text")
            assert bytes_written == len(content)

            # Verify content
            read_content = read_file(test_file, mode="text")
            assert read_content == content
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_text_size_limit_exceeded(self):
        """Test text write exceeding size limits fails."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/large_text.txt"

        # Content exceeding limit
        content = "x" * (MAX_TEXT_CHARS + 1)

        try:
            with pytest.raises(ValueError) as exc_info:
                write_file(test_file, content, mode="text")

            assert "FILE_SIZE_EXCEEDED" in str(exc_info.value)
            assert f"{MAX_TEXT_CHARS} chars" in str(exc_info.value)
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_binary_size_limit_within_bounds(self):
        """Test binary write within size limits succeeds."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/small_binary.bin"

        # Content within limit (5MB)
        content = b"x" * (1024 * 1024)  # 1MB

        try:
            bytes_written = write_file(test_file, content, mode="binary")
            assert bytes_written == len(content)

            # Verify content
            read_content = read_file(test_file, mode="binary")
            assert read_content == content
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_binary_size_limit_exceeded(self):
        """Test binary write exceeding size limits fails."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/large_binary.bin"

        # Content exceeding limit (>5MB)
        content = b"x" * (MAX_BINARY_BYTES + 1)

        try:
            with pytest.raises(ValueError) as exc_info:
                write_file(test_file, content, mode="binary")

            assert "FILE_SIZE_EXCEEDED" in str(exc_info.value)
            assert "5MB" in str(exc_info.value)
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")


class TestFileOverwritePolicy:
    """Test overwrite policy and collision detection."""

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_overwrite_false_existing_file_fails(self):
        """Test that existing file blocks write when overwrite=False."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/existing.txt"

        # Create existing file
        with open(test_file, "w") as f:
            f.write("original")

        try:
            # Attempt to write without overwrite should fail
            with pytest.raises(PermissionError) as exc_info:
                write_file(test_file, "new content", mode="text", overwrite=False)

            assert "FILE_EXISTS" in str(exc_info.value)
            assert "overwrite=False" in str(exc_info.value)

            # Verify original content unchanged
            with open(test_file, "r") as f:
                assert f.read() == "original"
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_overwrite_true_existing_file_succeeds(self):
        """Test that existing file is overwritten when overwrite=True."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/existing.txt"

        # Create existing file
        with open(test_file, "w") as f:
            f.write("original")

        try:
            # Write with overwrite should succeed
            bytes_written = write_file(test_file, "new content", mode="text", overwrite=True)
            assert bytes_written == len("new content")

            # Verify new content
            content = read_file(test_file, mode="text")
            assert content == "new content"
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")


class TestContentTypeValidation:
    """Test content type validation for text/binary modes."""

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_text_mode_requires_string(self):
        """Test that text mode requires string content."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/test.txt"

        try:
            # Bytes content in text mode should fail
            with pytest.raises(ValueError) as exc_info:
                write_file(test_file, b"bytes content", mode="text")

            assert "CONTENT_TYPE_MISMATCH" in str(exc_info.value)
            assert "Expected str for text mode" in str(exc_info.value)
        finally:
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_binary_mode_requires_bytes(self):
        """Test that binary mode requires bytes content."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)
        test_file = "/tmp/test-allowed/test.bin"

        try:
            # String content in binary mode should fail
            with pytest.raises(ValueError) as exc_info:
                write_file(test_file, "string content", mode="binary")

            assert "CONTENT_TYPE_MISMATCH" in str(exc_info.value)
            assert "Expected bytes for binary mode" in str(exc_info.value)
        finally:
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")


class TestConcurrentWrite:
    """Test concurrent write scenarios and atomic operations."""

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_concurrent_write_different_files(self):
        """Test concurrent writes to different files succeed."""
        os.makedirs("/tmp/test-allowed", exist_ok=True)

        results = []
        exceptions = []

        def write_worker(file_suffix, content):
            try:
                test_file = f"/tmp/test-allowed/concurrent_{file_suffix}.txt"
                bytes_written = write_file(test_file, content, mode="text")
                results.append((file_suffix, bytes_written))
            except Exception as e:
                exceptions.append((file_suffix, e))

        # Start concurrent writes
        threads = []
        for i in range(3):
            content = f"content_{i}" * 100
            thread = threading.Thread(target=write_worker, args=(i, content))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        try:
            # All writes should succeed
            assert len(exceptions) == 0, f"Unexpected exceptions: {exceptions}"
            assert len(results) == 3

            # Verify all files exist with correct content
            for i in range(3):
                test_file = f"/tmp/test-allowed/concurrent_{i}.txt"
                assert os.path.exists(test_file)
                content = read_file(test_file, mode="text")
                assert content == f"content_{i}" * 100
        finally:
            # Cleanup
            for i in range(3):
                test_file = f"/tmp/test-allowed/concurrent_{i}.txt"
                if os.path.exists(test_file):
                    os.unlink(test_file)
            if os.path.exists("/tmp/test-allowed"):
                os.rmdir("/tmp/test-allowed")


class TestMCPErrorFormat:
    """Test MCP error block formatting and error handling."""

    @patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"])
    def test_mcp_error_format_structure(self):
        """Test that errors follow MCP block format."""
        try:
            # Trigger access denied error
            read_file("/forbidden/path.txt", mode="text")
        except PermissionError as e:
            error_str = str(e)

            # Check MCP error block structure
            assert "---MCP_ERROR_START---" in error_str
            assert "---MCP_ERROR_END---" in error_str
            assert "identifier: FILE_ACCESS_DENIED" in error_str
            assert "message:" in error_str
            assert "stack:" in error_str
            assert "ipucu:" in error_str

    def test_file_not_found_error_format(self):
        """Test file not found error follows MCP format."""
        with patch("utils.file_io.ALLOWED_DIRS", ["/tmp/test-allowed"]):
            os.makedirs("/tmp/test-allowed", exist_ok=True)

            try:
                # Trigger file not found error
                read_file("/tmp/test-allowed/nonexistent.txt", mode="text")
            except FileNotFoundError as e:
                error_str = str(e)

                # Check MCP error format
                assert "identifier: FILE_NOT_FOUND" in error_str
                assert "File not found" in error_str
            finally:
                if os.path.exists("/tmp/test-allowed"):
                    os.rmdir("/tmp/test-allowed")


# Integration test fixtures
@pytest.fixture
def temp_allowed_dir():
    """Create temporary allowed directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="file_io_test_")
    with patch("utils.file_io.ALLOWED_DIRS", [temp_dir]):
        yield temp_dir
    # Cleanup
    import shutil

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
