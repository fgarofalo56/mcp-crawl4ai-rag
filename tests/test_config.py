"""
Unit tests for configuration module.

Tests configuration constants, environment variable handling,
and configuration helpers.
"""

import os

import pytest

from src.config import (
    REQUIRED_ENV_VARS,
    crawl_config,
    database_config,
    embedding_config,
    get_config_summary,
    get_env_with_default,
    get_required_env,
    llm_config,
    logging_config,
    validate_required_env_vars,
    validation_config,
)


class TestCrawlConfig:
    """Test crawl configuration."""

    def test_default_chunk_size(self):
        """Test default chunk size is set correctly."""
        assert crawl_config.DEFAULT_CHUNK_SIZE == 5000

    def test_max_concurrent_browsers(self):
        """Test max concurrent browsers is reasonable."""
        assert 1 <= crawl_config.MAX_CONCURRENT_BROWSERS <= 50

    def test_depth_limits(self):
        """Test depth limits are valid."""
        assert crawl_config.MIN_DEPTH_LIMIT < crawl_config.MAX_DEPTH_LIMIT
        assert crawl_config.MIN_DEPTH_LIMIT >= 1
        assert crawl_config.MAX_DEPTH >= crawl_config.MIN_DEPTH_LIMIT


class TestEmbeddingConfig:
    """Test embedding configuration."""

    def test_embedding_dimension(self):
        """Test embedding dimension is valid."""
        assert embedding_config.EMBEDDING_DIMENSION == 1536

    def test_batch_size(self):
        """Test batch size is reasonable."""
        assert 1 <= embedding_config.EMBEDDING_BATCH_SIZE <= 1000


class TestDatabaseConfig:
    """Test database configuration."""

    def test_table_names(self):
        """Test table names are set."""
        assert database_config.CRAWLED_PAGES_TABLE
        assert database_config.CODE_EXAMPLES_TABLE

    def test_retry_config(self):
        """Test retry configuration is valid."""
        assert database_config.MAX_DB_RETRIES >= 1
        assert database_config.INITIAL_RETRY_DELAY > 0
        assert database_config.RETRY_BACKOFF_FACTOR >= 1.0


class TestEnvironmentHelpers:
    """Test environment variable helper functions."""

    def test_get_env_with_default_missing(self):
        """Test getting missing env var returns default."""
        value = get_env_with_default("NONEXISTENT_VAR_12345", "default_value")
        assert value == "default_value"

    def test_get_env_with_default_present(self):
        """Test getting present env var returns actual value."""
        os.environ["TEST_VAR_EXISTS"] = "actual_value"
        value = get_env_with_default("TEST_VAR_EXISTS", "default_value")
        assert value == "actual_value"
        del os.environ["TEST_VAR_EXISTS"]

    def test_get_required_env_missing(self):
        """Test getting missing required env var raises error."""
        with pytest.raises(ValueError, match="not set"):
            get_required_env("NONEXISTENT_REQUIRED_VAR_12345")

    def test_get_required_env_present(self):
        """Test getting present required env var returns value."""
        os.environ["TEST_REQUIRED_VAR"] = "required_value"
        value = get_required_env("TEST_REQUIRED_VAR")
        assert value == "required_value"
        del os.environ["TEST_REQUIRED_VAR"]


class TestValidateRequiredEnvVars:
    """Test environment variable validation."""

    def test_validate_with_missing_vars(self, monkeypatch):
        """Test validation fails with missing variables."""
        # Clear all required env vars
        for var in REQUIRED_ENV_VARS:
            monkeypatch.delenv(var, raising=False)

        all_present, missing = validate_required_env_vars()
        assert not all_present
        assert len(missing) == len(REQUIRED_ENV_VARS)

    def test_validate_with_all_vars(self, monkeypatch):
        """Test validation succeeds with all variables."""
        # Set all required env vars
        for var in REQUIRED_ENV_VARS:
            monkeypatch.setenv(var, "test_value")

        all_present, missing = validate_required_env_vars()
        assert all_present
        assert len(missing) == 0


class TestConfigSummary:
    """Test configuration summary."""

    def test_get_config_summary_structure(self):
        """Test config summary has expected structure."""
        summary = get_config_summary()

        assert "crawl" in summary
        assert "embedding" in summary
        assert "database" in summary
        assert "logging" in summary

    def test_get_config_summary_values(self):
        """Test config summary contains expected values."""
        summary = get_config_summary()

        assert summary["crawl"]["chunk_size"] == crawl_config.DEFAULT_CHUNK_SIZE
        assert summary["embedding"]["dimension"] == embedding_config.EMBEDDING_DIMENSION
        assert summary["database"]["batch_size"] == database_config.SUPABASE_BATCH_SIZE
