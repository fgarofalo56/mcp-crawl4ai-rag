"""
Input validation utilities for MCP tools.

Provides validators for common input types used in MCP tools,
ensuring data quality and preventing errors.
"""

from typing import Optional, Any, Union
from pathlib import Path
from .config import crawl_config
from .error_handlers import ValidationError, validate_url, validate_range, validate_file_path


class InputValidator:
    """Validates inputs for MCP tools."""
    
    @staticmethod
    def validate_url_input(url: str) -> str:
        """
        Validate URL input for crawling.
        
        Args:
            url: URL to validate
            
        Returns:
            Cleaned URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL is required")
        
        url = url.strip()
        is_valid, error = validate_url(url)
        
        if not is_valid:
            raise ValidationError(error)
        
        return url
    
    @staticmethod
    def validate_depth(depth: int) -> int:
        """
        Validate crawl depth parameter.
        
        Args:
            depth: Crawl depth
            
        Returns:
            Validated depth
            
        Raises:
            ValidationError: If depth is invalid
        """
        is_valid, error = validate_range(
            depth,
            min_val=crawl_config.MIN_DEPTH_LIMIT,
            max_val=crawl_config.MAX_DEPTH_LIMIT,
            field_name="max_depth"
        )
        
        if not is_valid:
            raise ValidationError(error)
        
        return depth
    
    @staticmethod
    def validate_chunk_size(chunk_size: int) -> int:
        """
        Validate chunk size parameter.
        
        Args:
            chunk_size: Chunk size in characters
            
        Returns:
            Validated chunk size
            
        Raises:
            ValidationError: If chunk size is invalid
        """
        is_valid, error = validate_range(
            chunk_size,
            min_val=100,
            max_val=50000,
            field_name="chunk_size"
        )
        
        if not is_valid:
            raise ValidationError(error)
        
        return chunk_size
    
    @staticmethod
    def validate_concurrent_limit(limit: int) -> int:
        """
        Validate concurrent operations limit.
        
        Args:
            limit: Concurrent operations limit
            
        Returns:
            Validated limit
            
        Raises:
            ValidationError: If limit is invalid
        """
        is_valid, error = validate_range(
            limit,
            min_val=1,
            max_val=50,
            field_name="max_concurrent"
        )
        
        if not is_valid:
            raise ValidationError(error)
        
        return limit
    
    @staticmethod
    def validate_script_path(script_path: str) -> str:
        """
        Validate Python script path.
        
        Args:
            script_path: Path to Python script
            
        Returns:
            Validated path
            
        Raises:
            ValidationError: If path is invalid
        """
        is_valid, error = validate_file_path(script_path, must_exist=True)
        
        if not is_valid:
            raise ValidationError(error)
        
        # Check if it's a Python file
        if not script_path.endswith('.py'):
            raise ValidationError("Script must be a Python (.py) file")
        
        return script_path
    
    @staticmethod
    def validate_repo_url(repo_url: str) -> str:
        """
        Validate GitHub repository URL.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not repo_url:
            raise ValidationError("Repository URL is required")
        
        repo_url = repo_url.strip()
        
        # Basic URL validation
        is_valid, error = validate_url(repo_url)
        if not is_valid:
            raise ValidationError(error)
        
        # Check if it looks like a GitHub URL
        if 'github.com' not in repo_url.lower():
            raise ValidationError("URL must be a GitHub repository URL")
        
        # Check if it ends with .git
        if not repo_url.endswith('.git') and '/tree/' not in repo_url:
            # Add .git if missing
            if not repo_url.endswith('/'):
                repo_url += '.git'
            else:
                repo_url += '.git'
        
        return repo_url
    
    @staticmethod
    def validate_match_count(count: int) -> int:
        """
        Validate match count for search results.
        
        Args:
            count: Number of matches to return
            
        Returns:
            Validated count
            
        Raises:
            ValidationError: If count is invalid
        """
        is_valid, error = validate_range(
            count,
            min_val=1,
            max_val=100,
            field_name="match_count"
        )
        
        if not is_valid:
            raise ValidationError(error)
        
        return count
    
    @staticmethod
    def validate_source_filter(source: Optional[str]) -> Optional[str]:
        """
        Validate source filter parameter.
        
        Args:
            source: Source domain or identifier
            
        Returns:
            Validated source (or None if empty)
        """
        if not source or not source.strip():
            return None
        
        return source.strip()
    
    @staticmethod
    def validate_query(query: str, min_length: int = 1) -> str:
        """
        Validate search query.
        
        Args:
            query: Search query string
            min_length: Minimum query length
            
        Returns:
            Validated query
            
        Raises:
            ValidationError: If query is invalid
        """
        if not query or not query.strip():
            raise ValidationError("Query is required and cannot be empty")
        
        query = query.strip()
        
        if len(query) < min_length:
            raise ValidationError(f"Query must be at least {min_length} characters")
        
        return query
    
    @staticmethod
    def validate_command(command: str, allowed_commands: list[str]) -> str:
        """
        Validate command against allowed list.
        
        Args:
            command: Command to validate
            allowed_commands: List of allowed commands
            
        Returns:
            Validated command
            
        Raises:
            ValidationError: If command is invalid
        """
        if not command or not command.strip():
            raise ValidationError("Command is required")
        
        command = command.strip()
        
        if command not in allowed_commands:
            raise ValidationError(
                f"Invalid command: {command}. "
                f"Allowed commands: {', '.join(allowed_commands)}"
            )
        
        return command


# Convenience function for validating MCP tool inputs
def validate_mcp_tool_input(
    url: Optional[str] = None,
    depth: Optional[int] = None,
    chunk_size: Optional[int] = None,
    script_path: Optional[str] = None,
    repo_url: Optional[str] = None,
    query: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Validate multiple MCP tool inputs at once.
    
    Args:
        url: URL to validate
        depth: Depth to validate
        chunk_size: Chunk size to validate
        script_path: Script path to validate
        repo_url: Repository URL to validate
        query: Query to validate
        **kwargs: Additional parameters to validate
        
    Returns:
        Dictionary of validated inputs
        
    Raises:
        ValidationError: If any input is invalid
    """
    validator = InputValidator()
    validated = {}
    
    if url is not None:
        validated['url'] = validator.validate_url_input(url)
    
    if depth is not None:
        validated['depth'] = validator.validate_depth(depth)
    
    if chunk_size is not None:
        validated['chunk_size'] = validator.validate_chunk_size(chunk_size)
    
    if script_path is not None:
        validated['script_path'] = validator.validate_script_path(script_path)
    
    if repo_url is not None:
        validated['repo_url'] = validator.validate_repo_url(repo_url)
    
    if query is not None:
        validated['query'] = validator.validate_query(query)
    
    # Pass through other kwargs
    validated.update(kwargs)
    
    return validated
