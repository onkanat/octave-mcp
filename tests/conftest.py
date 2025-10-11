"""
Minimal test configuration and fixtures for Octave MCP.
"""

import asyncio
import pytest
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, AsyncMock
import tempfile


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def mock_session():
    """Provide a mock session for testing."""
    session = Mock()
    session.session_id = "test_session_123"
    session.workspace = {}
    session.created_at = "2024-01-01T00:00:00Z"
    session.last_accessed = "2024-01-01T00:00:00Z"
    return session


@pytest.fixture
def mock_async_client():
    """Provide a mock async HTTP client."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def sample_octave_code():
    """Provide sample Octave code for testing."""
    return """
    % Sample Octave code
    x = 1:10;
    y = x.^2;
    plot(x, y);
    title('Square function');
    """


@pytest.fixture
def sample_code_snippets():
    """Provide various code snippets for testing."""
    return {
        "simple": "x = 42;",
        "plot": "x = 1:100; plot(x, sin(x));",
        "function": """
        function y = square(x)
            y = x.^2;
        end
        """,
        "dangerous": "system('rm -rf /')",
        "loop": "for i = 1:10; x(i) = i^2; end",
    }


@pytest.fixture
def test_data_files(temp_dir):
    """Create test data files."""
    files = {}

    # Create sample .m file
    m_file = temp_dir / "test_script.m"
    m_file.write_text("x = 1:5; y = x.^2; plot(x, y);")
    files["octave_script"] = m_file

    # Create sample text file
    txt_file = temp_dir / "data.txt"
    txt_file.write_text("1 2 3\n4 5 6\n7 8 9\n")
    files["data_file"] = txt_file

    return files


@pytest.fixture
def mock_subprocess():
    """Provide mock subprocess for testing."""
    process = Mock()
    process.communicate.return_value = (b"output", b"")
    process.returncode = 0
    return process


# Markers for different test types
pytest_plugins = []

# Test markers
pytest.mark.unit = pytest.mark.mark("unit")
pytest.mark.integration = pytest.mark.mark("integration")
pytest.mark.contract = pytest.mark.mark("contract")
pytest.mark.slow = pytest.mark.mark("slow")
pytest.mark.network = pytest.mark.mark("network")
