"""
Unit tests for configuration utilities.
"""

import os
from unittest.mock import patch

from src.utils.config import get_env_int, get_env_bool, get_env_str, get_env_float


class TestEnvironmentUtils:
    """Test environment variable utility functions."""

    def test_get_env_int_default(self):
        """Test get_env_int with default value."""
        # Non-existent env var should return default
        result = get_env_int("NONEXISTENT_INT", 42)
        assert result == 42

    @patch.dict(os.environ, {"TEST_INT": "123"})
    def test_get_env_int_from_env(self):
        """Test get_env_int from environment."""
        result = get_env_int("TEST_INT", 0)
        assert result == 123

    @patch.dict(os.environ, {"INVALID_INT": "not_a_number"})
    def test_get_env_int_invalid(self):
        """Test get_env_int with invalid value."""
        result = get_env_int("INVALID_INT", 42)
        assert result == 42  # Should return default

    def test_get_env_bool_default(self):
        """Test get_env_bool with default value."""
        result = get_env_bool("NONEXISTENT_BOOL", False)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "true"})
    def test_get_env_bool_true_values(self):
        """Test get_env_bool with true values."""
        true_values = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]

        for value in true_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = get_env_bool("TEST_BOOL", False)
                assert result is True, f"Value '{value}' should be True"

    @patch.dict(os.environ, {"TEST_BOOL_FALSE": "false"})
    def test_get_env_bool_false_values(self):
        """Test get_env_bool with false values."""
        false_values = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]

        for value in false_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = get_env_bool("TEST_BOOL", True)
                assert result is False, f"Value '{value}' should be False"

    def test_get_env_str_default(self):
        """Test get_env_str with default value."""
        result = get_env_str("NONEXISTENT_STR", "default")
        assert result == "default"

    @patch.dict(os.environ, {"TEST_STR": "hello"})
    def test_get_env_str_from_env(self):
        """Test get_env_str from environment."""
        result = get_env_str("TEST_STR", "default")
        assert result == "hello"

    def test_get_env_str_none_default(self):
        """Test get_env_str with None default."""
        result = get_env_str("NONEXISTENT_STR")
        assert result is None

    def test_get_env_float_default(self):
        """Test get_env_float with default value."""
        result = get_env_float("NONEXISTENT_FLOAT", 3.14)
        assert result == 3.14

    @patch.dict(os.environ, {"TEST_FLOAT": "2.718"})
    def test_get_env_float_from_env(self):
        """Test get_env_float from environment."""
        result = get_env_float("TEST_FLOAT", 0.0)
        assert result == 2.718

    @patch.dict(os.environ, {"INVALID_FLOAT": "not_a_float"})
    def test_get_env_float_invalid(self):
        """Test get_env_float with invalid value."""
        result = get_env_float("INVALID_FLOAT", 1.23)
        assert result == 1.23  # Should return default

    @patch.dict(os.environ, {"EMPTY_STR": ""})
    def test_get_env_str_empty(self):
        """Test get_env_str with empty string."""
        result = get_env_str("EMPTY_STR", "default")
        assert result == ""

    @patch.dict(os.environ, {"WHITESPACE_BOOL": "  true  "})
    def test_get_env_bool_whitespace(self):
        """Test get_env_bool handles whitespace."""
        result = get_env_bool("WHITESPACE_BOOL", False)
        assert result is True


class TestConfigIntegration:
    """Integration tests for configuration utilities."""

    @patch.dict(
        os.environ,
        {"DEBUG": "true", "MAX_WORKERS": "8", "TIMEOUT": "30.5", "SERVICE_NAME": "octave-mcp"},
    )
    def test_mixed_environment_types(self):
        """Test reading different types from environment."""
        debug = get_env_bool("DEBUG", False)
        workers = get_env_int("MAX_WORKERS", 1)
        timeout = get_env_float("TIMEOUT", 10.0)
        service = get_env_str("SERVICE_NAME", "unknown")

        assert debug is True
        assert workers == 8
        assert timeout == 30.5
        assert service == "octave-mcp"

    def test_default_values_when_no_env(self):
        """Test that defaults work when no environment variables are set."""
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            debug = get_env_bool("DEBUG", False)
            workers = get_env_int("MAX_WORKERS", 4)
            timeout = get_env_float("TIMEOUT", 15.0)
            service = get_env_str("SERVICE_NAME", "default-service")

            assert debug is False
            assert workers == 4
            assert timeout == 15.0
            assert service == "default-service"

    @patch.dict(
        os.environ,
        {"CASE_TEST_1": "True", "CASE_TEST_2": "FALSE", "CASE_TEST_3": "Yes", "CASE_TEST_4": "no"},
    )
    def test_case_insensitive_booleans(self):
        """Test that boolean parsing is case insensitive."""
        assert get_env_bool("CASE_TEST_1", False) is True
        assert get_env_bool("CASE_TEST_2", True) is False
        assert get_env_bool("CASE_TEST_3", False) is True
        assert get_env_bool("CASE_TEST_4", True) is False
