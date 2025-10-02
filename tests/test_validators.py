"""
Unit tests for input validators.

Tests validation of URLs, depths, paths, queries, and other MCP tool inputs.
"""

import pytest
from src.validators import InputValidator, validate_mcp_tool_input
from src.error_handlers import ValidationError


class TestURLValidation:
    """Test URL validation."""
    
    def test_valid_http_url(self):
        """Test validating HTTP URL."""
        validator = InputValidator()
        url = validator.validate_url_input("http://example.com")
        assert url == "http://example.com"
    
    def test_valid_https_url(self):
        """Test validating HTTPS URL."""
        validator = InputValidator()
        url = validator.validate_url_input("https://example.com/path")
        assert url == "https://example.com/path"
    
    def test_invalid_empty_url(self):
        """Test validating empty URL raises error."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="required"):
            validator.validate_url_input("")
    
    def test_invalid_url_protocol(self):
        """Test validating URL with wrong protocol."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="http"):
            validator.validate_url_input("ftp://example.com")
    
    def test_url_whitespace_stripped(self):
        """Test URL whitespace is stripped."""
        validator = InputValidator()
        url = validator.validate_url_input("  https://example.com  ")
        assert url == "https://example.com"


class TestDepthValidation:
    """Test crawl depth validation."""
    
    def test_valid_depth(self):
        """Test validating valid depth."""
        validator = InputValidator()
        depth = validator.validate_depth(3)
        assert depth == 3
    
    def test_depth_too_low(self):
        """Test depth below minimum."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="must be >="):
            validator.validate_depth(0)
    
    def test_depth_too_high(self):
        """Test depth above maximum."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="must be <="):
            validator.validate_depth(20)


class TestChunkSizeValidation:
    """Test chunk size validation."""
    
    def test_valid_chunk_size(self):
        """Test validating valid chunk size."""
        validator = InputValidator()
        size = validator.validate_chunk_size(5000)
        assert size == 5000
    
    def test_chunk_size_too_small(self):
        """Test chunk size too small."""
        validator = InputValidator()
        with pytest.raises(ValidationError):
            validator.validate_chunk_size(50)
    
    def test_chunk_size_too_large(self):
        """Test chunk size too large."""
        validator = InputValidator()
        with pytest.raises(ValidationError):
            validator.validate_chunk_size(100000)


class TestScriptPathValidation:
    """Test script path validation."""
    
    def test_valid_script_path(self, tmp_path):
        """Test validating valid Python script path."""
        validator = InputValidator()
        script_file = tmp_path / "test_script.py"
        script_file.write_text("print('hello')")
        
        path = validator.validate_script_path(str(script_file))
        assert path == str(script_file)
    
    def test_script_path_not_exists(self):
        """Test script path that doesn't exist."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="not found"):
            validator.validate_script_path("/fake/path/script.py")
    
    def test_script_path_not_python(self, tmp_path):
        """Test script path that's not a Python file."""
        validator = InputValidator()
        text_file = tmp_path / "test.txt"
        text_file.write_text("not python")
        
        with pytest.raises(ValidationError, match="Python"):
            validator.validate_script_path(str(text_file))


class TestRepoURLValidation:
    """Test repository URL validation."""
    
    def test_valid_github_url(self):
        """Test validating GitHub URL."""
        validator = InputValidator()
        url = validator.validate_repo_url("https://github.com/user/repo.git")
        assert url == "https://github.com/user/repo.git"
    
    def test_github_url_without_git_suffix(self):
        """Test GitHub URL without .git suffix gets it added."""
        validator = InputValidator()
        url = validator.validate_repo_url("https://github.com/user/repo")
        assert url == "https://github.com/user/repo.git"
    
    def test_invalid_non_github_url(self):
        """Test non-GitHub URL raises error."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="GitHub"):
            validator.validate_repo_url("https://gitlab.com/user/repo")
    
    def test_empty_repo_url(self):
        """Test empty repo URL raises error."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="required"):
            validator.validate_repo_url("")


class TestQueryValidation:
    """Test search query validation."""
    
    def test_valid_query(self):
        """Test validating valid query."""
        validator = InputValidator()
        query = validator.validate_query("search term")
        assert query == "search term"
    
    def test_empty_query(self):
        """Test empty query raises error."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="required"):
            validator.validate_query("")
    
    def test_query_whitespace_stripped(self):
        """Test query whitespace is stripped."""
        validator = InputValidator()
        query = validator.validate_query("  search  ")
        assert query == "search"
    
    def test_query_minimum_length(self):
        """Test query minimum length validation."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="at least"):
            validator.validate_query("ab", min_length=3)


class TestMatchCountValidation:
    """Test match count validation."""
    
    def test_valid_match_count(self):
        """Test validating valid match count."""
        validator = InputValidator()
        count = validator.validate_match_count(10)
        assert count == 10
    
    def test_match_count_too_low(self):
        """Test match count below minimum."""
        validator = InputValidator()
        with pytest.raises(ValidationError):
            validator.validate_match_count(0)
    
    def test_match_count_too_high(self):
        """Test match count above maximum."""
        validator = InputValidator()
        with pytest.raises(ValidationError):
            validator.validate_match_count(200)


class TestSourceFilterValidation:
    """Test source filter validation."""
    
    def test_valid_source(self):
        """Test validating valid source."""
        validator = InputValidator()
        source = validator.validate_source_filter("example.com")
        assert source == "example.com"
    
    def test_empty_source_returns_none(self):
        """Test empty source returns None."""
        validator = InputValidator()
        source = validator.validate_source_filter("")
        assert source is None
        
        source = validator.validate_source_filter(None)
        assert source is None


class TestCommandValidation:
    """Test command validation."""
    
    def test_valid_command(self):
        """Test validating valid command."""
        validator = InputValidator()
        allowed = ["start", "stop", "restart"]
        cmd = validator.validate_command("start", allowed)
        assert cmd == "start"
    
    def test_invalid_command(self):
        """Test invalid command raises error."""
        validator = InputValidator()
        allowed = ["start", "stop"]
        with pytest.raises(ValidationError, match="Invalid command"):
            validator.validate_command("restart", allowed)
    
    def test_empty_command(self):
        """Test empty command raises error."""
        validator = InputValidator()
        with pytest.raises(ValidationError, match="required"):
            validator.validate_command("", ["start"])


class TestValidateMCPToolInput:
    """Test bulk MCP tool input validation."""
    
    def test_validate_multiple_inputs(self):
        """Test validating multiple inputs at once."""
        validated = validate_mcp_tool_input(
            url="https://example.com",
            depth=3,
            chunk_size=5000,
            query="search term"
        )
        
        assert validated["url"] == "https://example.com"
        assert validated["depth"] == 3
        assert validated["chunk_size"] == 5000
        assert validated["query"] == "search term"
    
    def test_validate_with_invalid_input(self):
        """Test validation fails with invalid input."""
        with pytest.raises(ValidationError):
            validate_mcp_tool_input(
                url="invalid-url",
                depth=3
            )
    
    def test_validate_with_extra_kwargs(self):
        """Test extra kwargs are passed through."""
        validated = validate_mcp_tool_input(
            url="https://example.com",
            custom_param="custom_value"
        )
        
        assert validated["url"] == "https://example.com"
        assert validated["custom_param"] == "custom_value"
