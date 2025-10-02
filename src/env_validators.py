"""
Environment variable validation and management.

Provides functions to validate, load, and manage environment variables
with proper error handling and type conversion.
"""

import os
from pathlib import Path
from typing import Optional, Any, Union
from dotenv import load_dotenv
from .config import (
    REQUIRED_ENV_VARS,
    OPTIONAL_ENV_VARS,
    ENV_FILE_NAME,
    HOME_ENV_FILE,
    get_required_env,
    get_env_with_default
)
from .logging_config import get_logger
from .error_handlers import ConfigurationError


logger = get_logger(__name__)


class EnvironmentManager:
    """Manages environment variables and configuration."""
    
    def __init__(self):
        """Initialize environment manager."""
        self._env_loaded = False
        self._validation_results = None
    
    def load_environment(
        self,
        env_file: Optional[Union[str, Path]] = None,
        search_paths: Optional[list[Path]] = None,
        override: bool = False
    ) -> bool:
        """
        Load environment variables from .env file.
        
        Searches for .env file in multiple locations:
        1. Specified env_file parameter
        2. Current working directory
        3. Script directory
        4. User home directory
        5. Custom search paths
        
        Args:
            env_file: Specific .env file path
            search_paths: Additional paths to search for .env file
            override: Whether to override existing environment variables
            
        Returns:
            True if .env file was found and loaded
        """
        loaded_from = None
        
        # Try specific file first
        if env_file:
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path, override=override)
                loaded_from = str(env_path)
                logger.info(f"Loaded environment from: {loaded_from}")
                self._env_loaded = True
                return True
        
        # Build search paths
        paths_to_try = [
            Path.cwd() / ENV_FILE_NAME,  # Current directory
            Path(__file__).parent.parent / ENV_FILE_NAME,  # Project root
            Path.home() / HOME_ENV_FILE,  # User home
        ]
        
        # Add custom search paths
        if search_paths:
            paths_to_try.extend([p / ENV_FILE_NAME for p in search_paths])
        
        # Try each path
        for path in paths_to_try:
            if path.exists():
                load_dotenv(path, override=override)
                loaded_from = str(path)
                logger.info(f"Loaded environment from: {loaded_from}")
                self._env_loaded = True
                return True
        
        logger.warning("No .env file found. Using system environment variables.")
        return False
    
    def validate_environment(self, raise_on_error: bool = True) -> tuple[bool, dict]:
        """
        Validate that all required environment variables are set.
        
        Args:
            raise_on_error: Whether to raise exception on validation failure
            
        Returns:
            Tuple of (all_valid, results_dict)
            
        Raises:
            ConfigurationError: If validation fails and raise_on_error=True
        """
        results = {
            "valid": True,
            "missing_required": [],
            "present_required": [],
            "optional_set": [],
            "optional_missing": [],
        }
        
        # Check required variables
        for var in REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value:
                results["present_required"].append(var)
            else:
                results["missing_required"].append(var)
                results["valid"] = False
        
        # Check optional variables
        for var in OPTIONAL_ENV_VARS.keys():
            if os.getenv(var):
                results["optional_set"].append(var)
            else:
                results["optional_missing"].append(var)
        
        self._validation_results = results
        
        # Log results
        if results["valid"]:
            logger.info(f"✓ All {len(results['present_required'])} required environment variables are set")
        else:
            logger.error(
                f"✗ Missing {len(results['missing_required'])} required environment variables: "
                f"{', '.join(results['missing_required'])}"
            )
        
        # Raise error if requested
        if not results["valid"] and raise_on_error:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(results['missing_required'])}"
            )
        
        return results["valid"], results
    
    def get_validation_summary(self) -> str:
        """
        Get a formatted summary of environment validation.
        
        Returns:
            Formatted string with validation results
        """
        if not self._validation_results:
            return "Environment validation has not been run yet."
        
        results = self._validation_results
        lines = []
        
        lines.append("=" * 60)
        lines.append("ENVIRONMENT VALIDATION SUMMARY")
        lines.append("=" * 60)
        
        # Required variables
        lines.append(f"\nRequired Variables ({len(REQUIRED_ENV_VARS)} total):")
        for var in results["present_required"]:
            value = os.getenv(var, "")
            masked = self._mask_value(value)
            lines.append(f"  ✓ {var}: {masked}")
        
        for var in results["missing_required"]:
            lines.append(f"  ✗ {var}: Not set")
        
        # Optional variables
        lines.append(f"\nOptional Variables ({len(OPTIONAL_ENV_VARS)} total):")
        for var in results["optional_set"]:
            value = os.getenv(var, "")
            masked = self._mask_value(value)
            lines.append(f"  ✓ {var}: {masked}")
        
        for var in results["optional_missing"]:
            default = OPTIONAL_ENV_VARS.get(var, "")
            lines.append(f"  ○ {var}: Using default ({default})")
        
        lines.append("\n" + "=" * 60)
        
        if results["valid"]:
            lines.append("Status: ✓ VALID - All required variables are set")
        else:
            lines.append("Status: ✗ INVALID - Missing required variables")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def _mask_value(value: str, show_chars: int = 8) -> str:
        """
        Mask a value for display (e.g., API keys).
        
        Args:
            value: Value to mask
            show_chars: Number of characters to show
            
        Returns:
            Masked value
        """
        if not value:
            return "Not set"
        
        if len(value) <= show_chars:
            return "***"
        
        return value[:show_chars] + "..."
    
    def get_env_int(
        self,
        var_name: str,
        default: Optional[int] = None,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None
    ) -> int:
        """
        Get environment variable as integer with validation.
        
        Args:
            var_name: Environment variable name
            default: Default value if not set
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Integer value
            
        Raises:
            ConfigurationError: If value is invalid
        """
        value_str = os.getenv(var_name)
        
        if value_str is None:
            if default is not None:
                return default
            raise ConfigurationError(f"Required environment variable '{var_name}' not set")
        
        try:
            value = int(value_str)
        except ValueError:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be an integer, got: {value_str}"
            )
        
        if min_val is not None and value < min_val:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be >= {min_val}, got: {value}"
            )
        
        if max_val is not None and value > max_val:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be <= {max_val}, got: {value}"
            )
        
        return value
    
    def get_env_float(
        self,
        var_name: str,
        default: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> float:
        """
        Get environment variable as float with validation.
        
        Args:
            var_name: Environment variable name
            default: Default value if not set
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Float value
            
        Raises:
            ConfigurationError: If value is invalid
        """
        value_str = os.getenv(var_name)
        
        if value_str is None:
            if default is not None:
                return default
            raise ConfigurationError(f"Required environment variable '{var_name}' not set")
        
        try:
            value = float(value_str)
        except ValueError:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be a number, got: {value_str}"
            )
        
        if min_val is not None and value < min_val:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be >= {min_val}, got: {value}"
            )
        
        if max_val is not None and value > max_val:
            raise ConfigurationError(
                f"Environment variable '{var_name}' must be <= {max_val}, got: {value}"
            )
        
        return value
    
    def get_env_bool(self, var_name: str, default: bool = False) -> bool:
        """
        Get environment variable as boolean.
        
        Accepts: true/false, yes/no, 1/0, on/off (case insensitive)
        
        Args:
            var_name: Environment variable name
            default: Default value if not set
            
        Returns:
            Boolean value
        """
        value_str = os.getenv(var_name)
        
        if value_str is None:
            return default
        
        value_str = value_str.lower().strip()
        
        if value_str in ('true', 'yes', '1', 'on'):
            return True
        elif value_str in ('false', 'no', '0', 'off', ''):
            return False
        else:
            logger.warning(
                f"Invalid boolean value for '{var_name}': {value_str}. "
                f"Using default: {default}"
            )
            return default


# Global environment manager instance
env_manager = EnvironmentManager()


# Convenience functions
def load_environment(**kwargs) -> bool:
    """Load environment variables. See EnvironmentManager.load_environment()."""
    return env_manager.load_environment(**kwargs)


def validate_environment(raise_on_error: bool = True) -> tuple[bool, dict]:
    """Validate environment variables. See EnvironmentManager.validate_environment()."""
    return env_manager.validate_environment(raise_on_error)


def get_validation_summary() -> str:
    """Get validation summary. See EnvironmentManager.get_validation_summary()."""
    return env_manager.get_validation_summary()


def get_env_int(var_name: str, default: Optional[int] = None, **kwargs) -> int:
    """Get environment variable as int. See EnvironmentManager.get_env_int()."""
    return env_manager.get_env_int(var_name, default, **kwargs)


def get_env_float(var_name: str, default: Optional[float] = None, **kwargs) -> float:
    """Get environment variable as float. See EnvironmentManager.get_env_float()."""
    return env_manager.get_env_float(var_name, default, **kwargs)


def get_env_bool(var_name: str, default: bool = False) -> bool:
    """Get environment variable as bool. See EnvironmentManager.get_env_bool()."""
    return env_manager.get_env_bool(var_name, default)
