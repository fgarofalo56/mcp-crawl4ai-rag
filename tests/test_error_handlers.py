"""
Unit tests for error handling utilities.

Tests error response creation, retry decorators, and validation helpers.
"""

import pytest
import json
import time
from src.error_handlers import (
    create_error_response,
    create_success_response,
    create_validation_error,
    retry_with_backoff,
    ValidationError,
    ConfigurationError,
    validate_url,
    validate_range,
    validate_file_path,
)


class TestErrorResponses:
    """Test error response creation."""
    
    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response("Something went wrong")
        data = json.loads(response)
        
        assert data["success"] is False
        assert data["error"] == "Something went wrong"
        assert data["error_type"] == "error"
    
    def test_create_error_response_with_extras(self):
        """Test creating error response with extra fields."""
        response = create_error_response(
            "Invalid input",
            error_type="validation_error",
            field="email",
            code=400
        )
        data = json.loads(response)
        
        assert data["error_type"] == "validation_error"
        assert data["field"] == "email"
        assert data["code"] == 400
    
    def test_create_success_response(self):
        """Test creating success response."""
        response = create_success_response({"result": "data"})
        data = json.loads(response)
        
        assert data["success"] is True
        assert data["result"] == "data"
    
    def test_create_validation_error(self):
        """Test creating validation error."""
        response = create_validation_error("email", "Invalid email format")
        data = json.loads(response)
        
        assert data["success"] is False
        assert data["error_type"] == "validation_error"
        assert data["field"] == "email"


class TestRetryDecorator:
    """Test retry decorator."""
    
    def test_retry_succeeds_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def succeed_immediately():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = succeed_immediately()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_succeeds_after_failures(self):
        """Test function succeeds after initial failures."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def succeed_on_third():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = succeed_on_third()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_fails_after_max_retries(self):
        """Test function fails after max retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fail()
        
        assert call_count == 3
    
    def test_retry_with_specific_exceptions(self):
        """Test retry only catches specified exceptions."""
        @retry_with_backoff(max_retries=3, initial_delay=0.01, exceptions=(ValueError,))
        def raise_type_error():
            raise TypeError("Wrong type")
        
        # TypeError should not be retried
        with pytest.raises(TypeError, match="Wrong type"):
            raise_type_error()


class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_validate_url_valid(self):
        """Test validating valid URLs."""
        valid, error = validate_url("https://example.com")
        assert valid is True
        assert error is None
        
        valid, error = validate_url("http://test.org/path")
        assert valid is True
        assert error is None
    
    def test_validate_url_invalid(self):
        """Test validating invalid URLs."""
        valid, error = validate_url("")
        assert valid is False
        assert error is not None
        
        valid, error = validate_url("not-a-url")
        assert valid is False
        assert error is not None
        
        valid, error = validate_url("ftp://wrong-protocol.com")
        assert valid is False
        assert error is not None
    
    def test_validate_range_valid(self):
        """Test validating values in range."""
        valid, error = validate_range(5, min_val=1, max_val=10)
        assert valid is True
        assert error is None
        
        valid, error = validate_range(1, min_val=1, max_val=10)
        assert valid is True
        
        valid, error = validate_range(10, min_val=1, max_val=10)
        assert valid is True
    
    def test_validate_range_invalid(self):
        """Test validating values out of range."""
        valid, error = validate_range(0, min_val=1, max_val=10)
        assert valid is False
        assert error is not None
        
        valid, error = validate_range(11, min_val=1, max_val=10)
        assert valid is False
        assert error is not None
    
    def test_validate_file_path_nonexistent(self, tmp_path):
        """Test validating nonexistent file."""
        fake_path = tmp_path / "nonexistent.txt"
        valid, error = validate_file_path(str(fake_path), must_exist=True)
        assert valid is False
        assert error is not None
    
    def test_validate_file_path_exists(self, tmp_path):
        """Test validating existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        valid, error = validate_file_path(str(test_file), must_exist=True)
        assert valid is True
        assert error is None


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid input")
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Missing config")
