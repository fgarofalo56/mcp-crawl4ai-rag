"""Crawl4AI MCP Server implementation."""

from .crawl4ai_mcp import mcp

# Import new utility modules for easy access
from .config import (
    crawl_config,
    embedding_config,
    database_config,
    llm_config,
    logging_config,
    validation_config,
    get_required_env,
    get_env_with_default,
)

from .logging_config import get_logger, setup_logging

from .error_handlers import (
    create_error_response,
    create_success_response,
    create_validation_error,
    retry_with_backoff,
    async_retry_with_backoff,
    ValidationError,
    ConfigurationError,
    DatabaseError,
    CrawlError,
)

from .env_validators import (
    load_environment,
    validate_environment,
    get_env_int,
    get_env_float,
    get_env_bool,
)

from .validators import (
    InputValidator,
    validate_mcp_tool_input,
)

__all__ = [
    # Main MCP server
    "mcp",
    # Configuration
    "crawl_config",
    "embedding_config",
    "database_config",
    "llm_config",
    "logging_config",
    "validation_config",
    "get_required_env",
    "get_env_with_default",
    # Logging
    "get_logger",
    "setup_logging",
    # Error handling
    "create_error_response",
    "create_success_response",
    "create_validation_error",
    "retry_with_backoff",
    "async_retry_with_backoff",
    "ValidationError",
    "ConfigurationError",
    "DatabaseError",
    "CrawlError",
    # Environment
    "load_environment",
    "validate_environment",
    "get_env_int",
    "get_env_float",
    "get_env_bool",
    # Validation
    "InputValidator",
    "validate_mcp_tool_input",
]
