"""
Modern test configuration and fixtures for Octave MCP.
"""

import asyncio
import tempfile
import pytest
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import Mock, AsyncMock
import httpx

from src.utils.config import Settings
from src.services.octave_runner import OctaveService
from src.services.publish_service import PublishService
from src.services.session_service import SessionService


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test-specific settings."""
    return Settings(
        api_host="127.0.0.1",
        api_port=8001,  # Different port for tests
        timeout_seconds=30,
        publish_dir="/tmp/test_publish",
        base_url="http://localhost:8001"
    )


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_publish_dir(temp_dir: Path) -> Path:
    """Provide a test publish directory."""
    publish_dir = temp_dir / "publish"
    publish_dir.mkdir(exist_ok=True)
    return publish_dir


# Service fixtures
@pytest.fixture
async def octave_service() -> AsyncGenerator[OctaveService, None]:
    """Provide a configured OctaveService instance."""
    service = OctaveService()
    yield service
    # Cleanup if service has cleanup method


@pytest.fixture
async def publish_service() -> PublishService:
    """Provide a configured PublishService instance."""
    return PublishService()


@pytest.fixture
async def session_service() -> SessionService:
    """Provide a configured SessionService instance."""
    return SessionService()


# Mock fixtures
@pytest.fixture
def mock_subprocess() -> Mock:
    """Provide a mock subprocess for testing."""
    mock = Mock()
    mock.run = Mock()
    mock.run.return_value = Mock(
        stdout="test output",
        stderr="",
        returncode=0
    )
    return mock


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Provide a mock httpx client for testing."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = "success"
    mock_client.post.return_value = mock_response
    mock_client.get.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_octave_code() -> str:
    """Provide sample Octave code for testing."""
    return """
    x = [1, 2, 3, 4, 5];
    y = x .^ 2;
    mean_y = mean(y);
    fprintf('Mean of squares: %.2f\\n', mean_y);
    """


@pytest.fixture
def sample_code_with_plot() -> str:
    """Provide sample Octave code that generates a plot."""
    return """
    x = 0:0.1:2*pi;
    y = sin(x);
    plot(x, y);
    title('Sine Wave');
    xlabel('x');
    ylabel('sin(x)');
    print('test_plot.png', '-dpng');
    """


@pytest.fixture
def sample_vectorization_code() -> str:
    """Provide sample code for vectorization analysis."""
    return """
    % Non-vectorized version
    result = zeros(1, 1000);
    for i = 1:1000
        result(i) = i^2 + 2*i + 1;
    end

    % Nested loops (should be flagged)
    matrix = zeros(100, 100);
    for i = 1:100
        for j = 1:100
            matrix(i, j) = i * j;
        end
    end
    """


# Test data fixtures
@pytest.fixture
def valid_run_request_data() -> Dict[str, Any]:
    """Provide valid run request data."""
    return {
        "code": "x = 1 + 1; disp(x);",
        "session_id": "test_session_123"
    }


@pytest.fixture
def valid_publish_request_data() -> Dict[str, Any]:
    """Provide valid publish request data."""
    return {
        "code": "x = 1:10; plot(x, x.^2); print('plot.png', '-dpng');",
        "session_id": "test_session_456"
    }


@pytest.fixture
def invalid_request_data() -> Dict[str, Any]:
    """Provide invalid request data for validation testing."""
    return {
        "code": "",  # Empty code should fail validation
        "session_id": "x" * 300  # Too long session ID
    }


# Error simulation fixtures
@pytest.fixture
def timeout_code() -> str:
    """Provide code that would timeout in normal execution."""
    return """
    % This would run indefinitely
    while true
        pause(1);
    end
    """


@pytest.fixture
def error_code() -> str:
    """Provide code that should generate an error."""
    return """
    % This should generate a syntax error
    x = [1, 2, 3
    y = x + ;
    """


@pytest.fixture
def memory_intensive_code() -> str:
    """Provide code that would use significant memory."""
    return """
    % This would use a lot of memory
    big_matrix = zeros(10000, 10000);
    for i = 1:10000
        big_matrix(i, :) = rand(1, 10000);
    end
    """


# API testing fixtures
@pytest.fixture
async def test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async test client for API testing."""
    async with httpx.AsyncClient(
        base_url="http://testserver"
    ) as client:
        yield client


# Database/State fixtures (for session testing)
@pytest.fixture
def clean_session_state():
    """Ensure clean session state for tests."""
    # This would clear any session storage
    yield
    # Cleanup after test


# Security testing fixtures
@pytest.fixture
def malicious_paths() -> list[str]:
    """Provide potentially malicious file paths for security testing."""
    return [
        "../../../etc/passwd",
        "/etc/passwd",
        "..\\..\\windows\\system32\\",
        "test/../../../secret.txt",
        "/tmp/../root/.ssh/id_rsa"
    ]


@pytest.fixture
def safe_paths() -> list[str]:
    """Provide safe file paths for testing."""
    return [
        "test_file.txt",
        "results/output.png",
        "data/input.csv",
        "/tmp/safe_file.txt"
    ]


# Performance testing fixtures
@pytest.fixture
def performance_test_data() -> Dict[str, Any]:
    """Provide data for performance testing."""
    return {
        "small_dataset": list(range(100)),
        "medium_dataset": list(range(10000)),
        "large_dataset": list(range(100000)),
        "test_iterations": 10
    }


# Marker helpers
def mark_slow(test_func):
    """Mark a test as slow running."""
    return pytest.mark.slow(test_func)


def mark_integration(test_func):
    """Mark a test as integration test."""
    return pytest.mark.integration(test_func)


def mark_external(test_func):
    """Mark a test as requiring external services."""
    return pytest.mark.external(test_func)
