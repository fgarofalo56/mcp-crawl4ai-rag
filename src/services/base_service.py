"""
Service Layer - Base Service Class

Provides base functionality for all service classes.
Services contain business logic extracted from MCP tools.
"""

import logging
from abc import ABC

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Base class for all services.

    Services encapsulate business logic and are independent of the MCP framework.
    This allows them to be tested without MCP context and reused in other contexts
    (CLI, API, background jobs, etc.).
    """

    def __init__(self):
        """Initialize base service."""
        self.logger = logger

    def _log_operation(self, operation: str, **kwargs):
        """Log service operation for debugging."""
        self.logger.info(f"{self.__class__.__name__}.{operation}", extra=kwargs)

    def _handle_error(self, error: Exception, context: dict) -> dict:
        """
        Standard error handling for service operations.

        Args:
            error: The exception that occurred
            context: Context information about the operation

        Returns:
            Standardized error response dict
        """
        self.logger.error(
            f"Error in {self.__class__.__name__}: {str(error)}", exc_info=True, extra=context
        )

        return {
            "success": False,
            "error": {"message": str(error), "type": type(error).__name__, "context": context},
        }
