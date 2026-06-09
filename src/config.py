"""
Configuration constants for the Crawl4AI MCP Server.

This module centralizes all configuration values, magic numbers, and settings
to improve maintainability and make the codebase easier to understand.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Final

# Environment File Configuration
ENV_FILE_NAME: Final[str] = ".env"
HOME_ENV_FILE: Final[str] = ".crawl4ai-rag.env"
ENV_FILE_ENCODING: Final[str] = "utf-8"

# Required Environment Variables
REQUIRED_ENV_VARS: Final[list[str]] = [
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
]

# Optional Environment Variables with Defaults
OPTIONAL_ENV_VARS: Final[dict[str, str]] = {
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "",
    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
    "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
}


@dataclass(frozen=True)
class CrawlConfig:
    """Crawling and scraping configuration."""

    # Chunk sizes
    DEFAULT_CHUNK_SIZE: int = 5000
    MAX_DOCUMENT_LENGTH: int = 25000
    CONTEXT_LENGTH: int = 500

    # Thresholds
    MIN_CHUNK_RATIO: float = 0.3
    MEMORY_THRESHOLD_PERCENT: float = 70.0

    # Concurrency
    DEFAULT_BATCH_SIZE: int = 20
    MAX_CONCURRENT_BROWSERS: int = 10
    MAX_CONCURRENT_CRAWLS: int = 10
    MAX_WORKERS: int = 10

    # Crawl limits
    MAX_DEPTH: int = 3
    MAX_DEPTH_LIMIT: int = 10
    MIN_DEPTH_LIMIT: int = 1

    # Timeouts (seconds)
    DEFAULT_TIMEOUT: int = 30
    LONG_TIMEOUT: int = 120
    CRAWLER_TIMEOUT: int = 120  # Timeout for web crawling operations
    API_TIMEOUT: int = 30  # Timeout for API calls (Azure OpenAI, etc.)
    DATABASE_TIMEOUT: int = 60  # Timeout for database operations


@dataclass(frozen=True)
class EmbeddingConfig:
    """Embedding and vector configuration."""

    EMBEDDING_DIMENSION: int = 1536
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Batch processing
    EMBEDDING_BATCH_SIZE: int = 100
    MAX_EMBEDDING_RETRIES: int = 3


@dataclass(frozen=True)
class DatabaseConfig:
    """Database and storage configuration."""

    # Supabase tables
    CRAWLED_PAGES_TABLE: str = "crawled_pages"
    CODE_EXAMPLES_TABLE: str = "code_examples"

    # Batch sizes
    SUPABASE_BATCH_SIZE: int = 20
    NEO4J_BATCH_SIZE: int = 100

    # Retry configuration
    MAX_DB_RETRIES: int = 3
    INITIAL_RETRY_DELAY: float = 1.0
    RETRY_BACKOFF_FACTOR: float = 2.0


@dataclass(frozen=True)
class LLMConfig:
    """LLM and completion configuration."""

    MAX_COMPLETION_TOKENS: int = 200
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 1.0

    # Azure OpenAI deployment names
    AZURE_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""

    DEFAULT_LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Log file settings
    LOG_DIR: str = "logs"
    LOG_FILE: str = "crawl4ai_mcp.log"
    MAX_LOG_SIZE: int = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT: int = 5


@dataclass(frozen=True)
class ValidationConfig:
    """Validation and hallucination detection configuration."""

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.5
    LOW_CONFIDENCE_THRESHOLD: float = 0.3

    # Analysis settings
    MAX_HALLUCINATIONS_BEFORE_FAIL: int = 10
    ENABLE_DETAILED_ANALYSIS: bool = True


# Global configuration instances
crawl_config = CrawlConfig()
embedding_config = EmbeddingConfig()
database_config = DatabaseConfig()
llm_config = LLMConfig()
logging_config = LoggingConfig()
validation_config = ValidationConfig()


# Default port range for MCP server
DEFAULT_MCP_PORT: Final[int] = 8051
MCP_PORT_RANGE_START: Final[int] = 8051
MCP_PORT_RANGE_END: Final[int] = 8100


def get_env_with_default(var_name: str, default: str = "") -> str:
    """
    Get environment variable with a default value.

    Args:
        var_name: Name of the environment variable
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(var_name, default)


def get_required_env(var_name: str) -> str:
    """
    Get required environment variable, raise error if not set.

    Args:
        var_name: Name of the environment variable

    Returns:
        Environment variable value

    Raises:
        ValueError: If environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        raise ValueError(
            f"Required environment variable '{var_name}' is not set. "
            f"Please set it in your .env file or system environment."
        )
    return value


def validate_required_env_vars() -> tuple[bool, list[str]]:
    """
    Validate that all required environment variables are set.

    Returns:
        Tuple of (all_present, missing_vars)
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    return len(missing) == 0, missing


def get_config_summary() -> dict[str, Any]:
    """
    Get a summary of current configuration.

    Returns:
        Dictionary with configuration summary
    """
    return {
        "crawl": {
            "chunk_size": crawl_config.DEFAULT_CHUNK_SIZE,
            "max_concurrent": crawl_config.MAX_CONCURRENT_BROWSERS,
            "max_depth": crawl_config.MAX_DEPTH,
        },
        "embedding": {
            "dimension": embedding_config.EMBEDDING_DIMENSION,
            "model": embedding_config.DEFAULT_EMBEDDING_MODEL,
        },
        "database": {
            "batch_size": database_config.SUPABASE_BATCH_SIZE,
            "max_retries": database_config.MAX_DB_RETRIES,
        },
        "logging": {
            "level": logging_config.DEFAULT_LOG_LEVEL,
            "log_dir": logging_config.LOG_DIR,
        },
    }
