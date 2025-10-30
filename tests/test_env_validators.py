"""Tests for environment variable validation and management."""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.env_validators import (
    EnvironmentManager,
    get_env_bool,
    get_env_float,
    get_env_int,
    load_environment,
    validate_environment,
)
from src.error_handlers import ConfigurationError


class TestEnvironmentManager:
    """Test EnvironmentManager class."""

    def test_init(self):
        """Test EnvironmentManager initialization."""
        em = EnvironmentManager()
        assert em._env_loaded is False
        assert em._validation_results is None

    def test_load_environment_from_file(self, tmp_path, monkeypatch):
        """Test loading environment from specific file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\n")

        em = EnvironmentManager()
        result = em.load_environment(env_file=str(env_file))

        assert result is True
        assert em._env_loaded is True
        assert os.getenv("TEST_VAR") == "test_value"

    def test_load_environment_file_not_found(self):
        """Test loading environment when file doesn't exist."""
        em = EnvironmentManager()
        result = em.load_environment(env_file="/nonexistent/.env")
        assert result is False

    def test_validate_environment_all_valid(self, monkeypatch):
        """Test environment validation with all required vars set."""
        # Set all required vars
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")

        em = EnvironmentManager()
        valid, results = em.validate_environment(raise_on_error=False)

        assert valid is True
        assert len(results["missing_required"]) == 0

    def test_validate_environment_missing_required(self, monkeypatch):
        """Test environment validation with missing required vars."""
        # Clear required vars
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

        em = EnvironmentManager()
        valid, results = em.validate_environment(raise_on_error=False)

        assert valid is False
        assert "SUPABASE_URL" in results["missing_required"]
        assert "SUPABASE_SERVICE_KEY" in results["missing_required"]

    def test_validate_environment_raises_error(self, monkeypatch):
        """Test environment validation raises error when configured."""
        monkeypatch.delenv("SUPABASE_URL", raising=False)

        em = EnvironmentManager()

        with pytest.raises(ConfigurationError):
            em.validate_environment(raise_on_error=True)

    def test_get_validation_summary_not_run(self):
        """Test get_validation_summary before validation."""
        em = EnvironmentManager()
        summary = em.get_validation_summary()

        assert "has not been run yet" in summary

    def test_get_validation_summary_after_validation(self, monkeypatch):
        """Test get_validation_summary after validation."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")

        em = EnvironmentManager()
        em.validate_environment(raise_on_error=False)
        summary = em.get_validation_summary()

        assert "ENVIRONMENT VALIDATION SUMMARY" in summary
        assert "SUPABASE_URL" in summary

    def test_mask_value_short(self):
        """Test value masking for short values."""
        masked = EnvironmentManager._mask_value("abc")
        assert masked == "***"

    def test_mask_value_long(self):
        """Test value masking for long values."""
        masked = EnvironmentManager._mask_value("this_is_a_long_api_key_value")
        assert masked.startswith("this_is_")
        assert masked.endswith("...")

    def test_mask_value_empty(self):
        """Test value masking for empty values."""
        masked = EnvironmentManager._mask_value("")
        assert masked == "Not set"

    def test_get_env_int_valid(self, monkeypatch):
        """Test getting integer environment variable."""
        monkeypatch.setenv("TEST_INT", "42")

        em = EnvironmentManager()
        value = em.get_env_int("TEST_INT")

        assert value == 42
        assert isinstance(value, int)

    def test_get_env_int_with_default(self):
        """Test getting integer with default value."""
        em = EnvironmentManager()
        value = em.get_env_int("NONEXISTENT_INT", default=10)

        assert value == 10

    def test_get_env_int_invalid(self, monkeypatch):
        """Test getting invalid integer raises error."""
        monkeypatch.setenv("TEST_INT", "not_a_number")

        em = EnvironmentManager()

        with pytest.raises(ConfigurationError):
            em.get_env_int("TEST_INT")

    def test_get_env_int_with_min_max(self, monkeypatch):
        """Test integer validation with min/max."""
        monkeypatch.setenv("TEST_INT", "50")

        em = EnvironmentManager()
        value = em.get_env_int("TEST_INT", min_val=0, max_val=100)

        assert value == 50

    def test_get_env_int_below_min(self, monkeypatch):
        """Test integer below minimum raises error."""
        monkeypatch.setenv("TEST_INT", "-5")

        em = EnvironmentManager()

        with pytest.raises(ConfigurationError):
            em.get_env_int("TEST_INT", min_val=0)

    def test_get_env_int_above_max(self, monkeypatch):
        """Test integer above maximum raises error."""
        monkeypatch.setenv("TEST_INT", "150")

        em = EnvironmentManager()

        with pytest.raises(ConfigurationError):
            em.get_env_int("TEST_INT", max_val=100)

    def test_get_env_float_valid(self, monkeypatch):
        """Test getting float environment variable."""
        monkeypatch.setenv("TEST_FLOAT", "3.14")

        em = EnvironmentManager()
        value = em.get_env_float("TEST_FLOAT")

        assert value == 3.14
        assert isinstance(value, float)

    def test_get_env_float_with_default(self):
        """Test getting float with default value."""
        em = EnvironmentManager()
        value = em.get_env_float("NONEXISTENT_FLOAT", default=2.5)

        assert value == 2.5

    def test_get_env_float_invalid(self, monkeypatch):
        """Test getting invalid float raises error."""
        monkeypatch.setenv("TEST_FLOAT", "not_a_number")

        em = EnvironmentManager()

        with pytest.raises(ConfigurationError):
            em.get_env_float("TEST_FLOAT")

    def test_get_env_bool_true_values(self, monkeypatch):
        """Test boolean true values."""
        em = EnvironmentManager()

        for value in ["true", "TRUE", "True", "yes", "YES", "1", "on", "ON"]:
            monkeypatch.setenv("TEST_BOOL", value)
            assert em.get_env_bool("TEST_BOOL") is True

    def test_get_env_bool_false_values(self, monkeypatch):
        """Test boolean false values."""
        em = EnvironmentManager()

        for value in ["false", "FALSE", "False", "no", "NO", "0", "off", "OFF", ""]:
            monkeypatch.setenv("TEST_BOOL", value)
            assert em.get_env_bool("TEST_BOOL") is False

    def test_get_env_bool_default(self):
        """Test boolean with default value."""
        em = EnvironmentManager()
        assert em.get_env_bool("NONEXISTENT_BOOL", default=True) is True
        assert em.get_env_bool("NONEXISTENT_BOOL", default=False) is False

    def test_get_env_bool_invalid_value(self, monkeypatch):
        """Test boolean with invalid value uses default."""
        monkeypatch.setenv("TEST_BOOL", "maybe")

        em = EnvironmentManager()
        result = em.get_env_bool("TEST_BOOL", default=True)

        assert result is True  # Falls back to default


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_load_environment(self, tmp_path, monkeypatch):
        """Test load_environment function."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_LOAD=loaded\n")

        result = load_environment(env_file=str(env_file))
        assert result is True

    def test_validate_environment(self, monkeypatch):
        """Test validate_environment function."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")

        valid, results = validate_environment(raise_on_error=False)
        assert valid is True

    def test_get_env_int_function(self, monkeypatch):
        """Test get_env_int convenience function."""
        monkeypatch.setenv("TEST_INT_FUNC", "100")
        value = get_env_int("TEST_INT_FUNC")
        assert value == 100

    def test_get_env_float_function(self, monkeypatch):
        """Test get_env_float convenience function."""
        monkeypatch.setenv("TEST_FLOAT_FUNC", "1.5")
        value = get_env_float("TEST_FLOAT_FUNC")
        assert value == 1.5

    def test_get_env_bool_function(self, monkeypatch):
        """Test get_env_bool convenience function."""
        monkeypatch.setenv("TEST_BOOL_FUNC", "true")
        value = get_env_bool("TEST_BOOL_FUNC")
        assert value is True
