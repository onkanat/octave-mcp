"""
Unit tests for configuration module.
"""

import os
import pytest
from unittest.mock import patch

from src.config.settings import Settings, get_settings


class TestSettings:
    """Test Settings model validation and behavior."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 8000
        assert settings.timeout_seconds == 60
        assert settings.publish_dir == "/tmp/octave_published"
        assert settings.base_url == "http://localhost:8000"

    def test_custom_settings(self):
        """Test custom settings initialization."""
        settings = Settings(
            api_host="0.0.0.0",
            api_port=9000,
            timeout_seconds=120,
            publish_dir="/custom/path",
            base_url="https://example.com",
        )

        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 9000
        assert settings.timeout_seconds == 120
        assert settings.publish_dir == "/custom/path"
        assert settings.base_url == "https://example.com"

    def test_port_validation(self):
        """Test port number validation."""
        # Valid ports
        settings = Settings(api_port=1)
        assert settings.api_port == 1

        settings = Settings(api_port=65535)
        assert settings.api_port == 65535

        # Invalid ports should raise validation error
        with pytest.raises(ValueError):
            Settings(api_port=0)

        with pytest.raises(ValueError):
            Settings(api_port=65536)

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeout
        settings = Settings(timeout_seconds=1)
        assert settings.timeout_seconds == 1

        # Zero timeout should be valid (no timeout)
        settings = Settings(timeout_seconds=0)
        assert settings.timeout_seconds == 0

        # Negative timeout should raise validation error
        with pytest.raises(ValueError):
            Settings(timeout_seconds=-1)

    @patch.dict(
        os.environ,
        {
            "API_HOST": "192.168.1.100",
            "API_PORT": "3000",
            "TIMEOUT_SECONDS": "90",
            "PUBLISH_DIR": "/env/publish",
            "BASE_URL": "http://192.168.1.100:3000",
        },
    )
    def test_environment_variables(self):
        """Test settings loading from environment variables."""
        settings = Settings()

        assert settings.api_host == "192.168.1.100"
        assert settings.api_port == 3000
        assert settings.timeout_seconds == 90
        assert settings.publish_dir == "/env/publish"
        assert settings.base_url == "http://192.168.1.100:3000"

    def test_field_descriptions(self):
        """Test that field descriptions are properly set."""
        settings = Settings()
        fields = settings.model_fields

        assert "API server host" in str(fields["api_host"].description)
        assert "API server port" in str(fields["api_port"].description)
        assert "timeout" in str(fields["timeout_seconds"].description).lower()

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        settings = Settings()

        # Pydantic models are immutable by default
        with pytest.raises(AttributeError):
            settings.api_port = 9999


class TestGetSettings:
    """Test the get_settings function and caching behavior."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_caching(self):
        """Test that get_settings caches the result."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should return the same instance due to caching
        assert settings1 is settings2

    @patch.dict(os.environ, {"API_PORT": "4000"})
    def test_get_settings_with_env_override(self):
        """Test get_settings with environment variable override."""
        # Clear cache to test environment loading
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.api_port == 4000

        # Clean up
        get_settings.cache_clear()

    def test_get_settings_cache_clearing(self):
        """Test that cache can be cleared properly."""
        settings1 = get_settings()
        get_settings.cache_clear()
        settings2 = get_settings()

        # After clearing cache, should get new instance
        assert settings1 is not settings2
        assert isinstance(settings2, Settings)


class TestSettingsValidation:
    """Test advanced validation features of Settings."""

    def test_model_validation_on_assignment(self):
        """Test that model validation works on field assignment."""
        with pytest.raises(ValueError):
            Settings(api_port="invalid_port")

    def test_settings_serialization(self):
        """Test that settings can be serialized to dict."""
        settings = Settings(api_port=8080)
        settings_dict = settings.model_dump()

        assert isinstance(settings_dict, dict)
        assert settings_dict["api_port"] == 8080
        assert "api_host" in settings_dict

    def test_settings_json_serialization(self):
        """Test that settings can be serialized to JSON."""
        settings = Settings()
        json_str = settings.model_dump_json()

        assert isinstance(json_str, str)
        assert '"api_port"' in json_str
        assert '"api_host"' in json_str

    def test_settings_from_dict(self):
        """Test creating settings from dictionary."""
        config_dict = {"api_host": "example.com", "api_port": 5000, "timeout_seconds": 45}

        settings = Settings(**config_dict)

        assert settings.api_host == "example.com"
        assert settings.api_port == 5000
        assert settings.timeout_seconds == 45


@pytest.mark.integration
class TestSettingsIntegration:
    """Integration tests for settings with the broader application."""

    def test_settings_with_real_paths(self, tmp_path):
        """Test settings with real filesystem paths."""
        publish_dir = str(tmp_path / "publish")

        settings = Settings(publish_dir=publish_dir)
        assert settings.publish_dir == publish_dir

    def test_settings_url_construction(self):
        """Test URL construction from settings."""
        settings = Settings(
            api_host="api.example.com", api_port=443, base_url="https://api.example.com"
        )

        # Test that settings provide correct values for URL construction
        expected_url = f"https://{settings.api_host}"
        assert settings.base_url.startswith("https://")
        assert settings.api_host in settings.base_url

    def test_settings_with_environment_file(self, tmp_path):
        """Test loading settings with environment file simulation."""
        # This would test .env file loading in a real scenario
        env_vars = {"API_HOST": "prod.example.com", "API_PORT": "8443", "TIMEOUT_SECONDS": "300"}

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.api_host == "prod.example.com"
            assert settings.api_port == 8443
            assert settings.timeout_seconds == 300
