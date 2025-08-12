# Code Style and Conventions

## Python Version
- Python 3.12+ required
- Modern Python features utilized (dataclasses, type hints, async/await)

## Code Style
- **Type Hints**: Extensive use of type hints throughout the codebase
  - Function parameters and return types are annotated
  - Uses `typing` module for complex types (List, Dict, Any, Optional, etc.)
  
- **Docstrings**: Comprehensive docstrings for all major functions and classes
  - Format: Multi-line docstrings with description, Args, and Returns sections
  - Example:
    ```python
    """
    Brief description of the function.
    
    Longer explanation if needed.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
    
    Returns:
        Description of return value
    """
    ```

- **Naming Conventions**:
  - Functions and variables: snake_case (e.g., `crawl_single_page`, `source_id`)
  - Classes: PascalCase (e.g., `AIScriptAnalyzer`, `KnowledgeGraphValidator`)
  - Constants: UPPER_SNAKE_CASE (e.g., `NEO4J_URI`)
  - Private/internal: Leading underscore (e.g., `_handle_repos_command`)

- **Imports**:
  - Standard library imports first
  - Third-party imports second
  - Local imports last
  - Grouped and alphabetically sorted within groups

- **Async/Await**: Heavy use of async functions for I/O operations
  - Main crawling functions are async
  - Concurrent processing with `asyncio` and `concurrent.futures`

- **Error Handling**:
  - Try-except blocks for all major operations
  - Detailed error messages returned in JSON format
  - Graceful degradation when optional features fail

- **Data Classes**: Extensive use of `@dataclass` decorator for data structures
  - Used in knowledge graph modules for structured data
  - Default factories for mutable defaults

## Code Organization
- **Modular Design**: Separate modules for different concerns
  - Main server logic in `crawl4ai_mcp.py`
  - Utility functions in `utils.py`
  - Knowledge graph functionality in separate modules
  
- **Decorator Usage**:
  - `@mcp.tool()` for MCP tool functions
  - `@dataclass` for data structures
  - `@asynccontextmanager` for lifecycle management

## Configuration
- Environment variables for all configuration
- `.env` file for local development
- Graceful fallbacks when optional features not configured