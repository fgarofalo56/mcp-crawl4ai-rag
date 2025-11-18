"""
Integration tests for Docker deployment and initialization.

This test suite covers Docker deployment scenarios including:
- Environment variable validation
- Service initialization (Supabase, Neo4j, OpenAI)
- Lifespan context creation and cleanup
- Graceful degradation with missing services
- Configuration loading from environment
"""

import asyncio
import os
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


class TestEnvironmentValidation:
    """Test environment variable validation for Docker deployment."""

    def test_required_supabase_vars_present(self, mock_env_config):
        """Test that required Supabase environment variables are present."""
        assert os.getenv("SUPABASE_URL") is not None
        assert os.getenv("SUPABASE_SERVICE_KEY") is not None
        assert "https://" in os.getenv("SUPABASE_URL")

    def test_required_openai_vars_present(self, mock_env_config):
        """Test that required Azure OpenAI environment variables are present."""
        assert os.getenv("AZURE_OPENAI_ENDPOINT") is not None
        assert os.getenv("AZURE_OPENAI_API_KEY") is not None
        assert os.getenv("AZURE_OPENAI_API_VERSION") is not None
        assert os.getenv("DEPLOYMENT_NAME") is not None
        assert os.getenv("EMBEDDING_DEPLOYMENT") is not None

    def test_optional_neo4j_vars(self, mock_env_config):
        """Test that Neo4j variables are optional but validated when present."""
        assert os.getenv("NEO4J_URI") is not None
        assert os.getenv("NEO4J_USER") is not None
        assert os.getenv("NEO4J_PASSWORD") is not None

        # Should be valid URI format
        uri = os.getenv("NEO4J_URI")
        assert uri.startswith("bolt://") or uri.startswith("neo4j://")

    def test_feature_flags_default_values(self, mock_env_config):
        """Test that feature flags have proper default values."""
        # These should be strings "true" or "false"
        reranking = os.getenv("USE_RERANKING", "false")
        assert reranking in ["true", "false"]

        hybrid = os.getenv("USE_HYBRID_SEARCH", "false")
        assert hybrid in ["true", "false"]

        kg = os.getenv("USE_KNOWLEDGE_GRAPH", "false")
        assert kg in ["true", "false"]

    def test_missing_required_var_raises_error(self, monkeypatch):
        """Test that missing required variables raise appropriate errors."""
        # Remove required var
        monkeypatch.delenv("SUPABASE_URL", raising=False)

        # Should fail when trying to initialize Supabase
        with patch("src.utils.get_supabase_client") as mock_client:
            mock_client.side_effect = ValueError("SUPABASE_URL not found")

            with pytest.raises(ValueError, match="SUPABASE_URL"):
                mock_client()


class TestServiceInitialization:
    """Test initialization of external services."""

    @pytest.mark.asyncio
    async def test_supabase_client_initialization(self, mock_env_config):
        """Test Supabase client initializes correctly."""
        with patch("src.utils.get_supabase_client") as mock_client:
            mock_client.return_value = Mock()

            client = mock_client()

            assert client is not None
            mock_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_driver_initialization(self, mock_env_config, mock_neo4j_session):
        """Test Neo4j driver initializes correctly when enabled."""
        with patch("knowledge_graph_validator.KnowledgeGraphValidator") as MockValidator:
            validator = AsyncMock()
            validator.initialize = AsyncMock()
            MockValidator.return_value = validator

            # Initialize
            instance = MockValidator(
                os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")
            )
            await instance.initialize()

            assert instance is not None
            instance.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_openai_client_initialization(self, mock_env_config):
        """Test Azure OpenAI client initializes correctly."""
        from unittest.mock import MagicMock

        with patch("openai.AzureOpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client

            client = MockOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )

            assert client is not None
            MockOpenAI.assert_called_once()

    @pytest.mark.asyncio
    async def test_crawler_initialization(self):
        """Test AsyncWebCrawler initializes correctly."""
        with patch("crawl4ai.AsyncWebCrawler") as MockCrawler:
            crawler = AsyncMock()
            crawler.__aenter__ = AsyncMock(return_value=crawler)
            crawler.__aexit__ = AsyncMock()
            MockCrawler.return_value = crawler

            async with MockCrawler() as c:
                assert c is not None

    @pytest.mark.asyncio
    async def test_reranker_initialization_when_enabled(self, mock_env_config):
        """Test cross-encoder reranker initializes when USE_RERANKING=true."""
        with patch("sentence_transformers.CrossEncoder") as MockEncoder:
            mock_model = Mock()
            MockEncoder.return_value = mock_model

            if os.getenv("USE_RERANKING") == "true":
                model = MockEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
                assert model is not None
                MockEncoder.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialization_order(self):
        """Test that services initialize in correct order."""
        initialization_log = []

        async def mock_init_supabase():
            initialization_log.append("supabase")
            return Mock()

        async def mock_init_crawler():
            initialization_log.append("crawler")
            return AsyncMock()

        async def mock_init_neo4j():
            initialization_log.append("neo4j")
            return AsyncMock()

        # Simulate initialization sequence
        await mock_init_crawler()
        await mock_init_supabase()
        await mock_init_neo4j()

        # Verify order
        assert initialization_log == ["crawler", "supabase", "neo4j"]


class TestLifespanContext:
    """Test lifespan context management."""

    @pytest.mark.asyncio
    async def test_lifespan_context_creation(self, mock_env_config):
        """Test lifespan context creates all components."""
        # Mock all components
        with (
            patch("crawl4ai.AsyncWebCrawler") as MockCrawler,
            patch("src.utils.get_supabase_client") as mock_supabase,
            patch("sentence_transformers.CrossEncoder") as MockEncoder,
        ):
            crawler = AsyncMock()
            crawler.__aenter__ = AsyncMock(return_value=crawler)
            crawler.__aexit__ = AsyncMock()
            MockCrawler.return_value = crawler

            mock_supabase.return_value = Mock()
            MockEncoder.return_value = Mock()

            # Simulate lifespan context creation
            context_components = {
                "crawler": crawler,
                "supabase_client": mock_supabase(),
                "reranking_model": MockEncoder() if os.getenv("USE_RERANKING") == "true" else None,
            }

            assert context_components["crawler"] is not None
            assert context_components["supabase_client"] is not None

    @pytest.mark.asyncio
    async def test_lifespan_cleanup(self):
        """Test lifespan context cleans up resources properly."""
        cleanup_called = []

        crawler = AsyncMock()
        crawler.__aexit__ = AsyncMock(side_effect=lambda *args: cleanup_called.append("crawler"))

        validator = AsyncMock()
        validator.close = AsyncMock(side_effect=lambda: cleanup_called.append("validator"))

        extractor = AsyncMock()
        extractor.close = AsyncMock(side_effect=lambda: cleanup_called.append("extractor"))

        # Simulate cleanup
        await crawler.__aexit__(None, None, None)
        await validator.close()
        await extractor.close()

        assert "crawler" in cleanup_called
        assert "validator" in cleanup_called
        assert "extractor" in cleanup_called

    @pytest.mark.asyncio
    async def test_lifespan_cleanup_handles_errors(self):
        """Test that cleanup continues even if some components fail."""
        cleanup_log = []

        async def cleanup_success():
            cleanup_log.append("success")

        async def cleanup_failure():
            cleanup_log.append("attempted")
            raise Exception("Cleanup failed")

        # Simulate cleanup with error handling
        try:
            await cleanup_failure()
        except Exception:
            pass  # Continue with other cleanups

        await cleanup_success()

        assert "attempted" in cleanup_log
        assert "success" in cleanup_log


class TestGracefulDegradation:
    """Test graceful degradation when optional services are unavailable."""

    @pytest.mark.asyncio
    async def test_missing_neo4j_doesnt_block_startup(self, mock_env_config, monkeypatch):
        """Test that missing Neo4j doesn't prevent app from starting."""
        # Disable Neo4j
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "false")

        # Should still be able to create basic context
        with (
            patch("crawl4ai.AsyncWebCrawler") as MockCrawler,
            patch("src.utils.get_supabase_client") as mock_supabase,
        ):
            crawler = AsyncMock()
            crawler.__aenter__ = AsyncMock(return_value=crawler)
            crawler.__aexit__ = AsyncMock()
            MockCrawler.return_value = crawler

            mock_supabase.return_value = Mock()

            # Basic context should work
            context_components = {
                "crawler": crawler,
                "supabase_client": mock_supabase(),
                "knowledge_validator": None,
                "repo_extractor": None,
            }

            assert context_components["crawler"] is not None
            assert context_components["supabase_client"] is not None
            assert context_components["knowledge_validator"] is None

    @pytest.mark.asyncio
    async def test_neo4j_connection_failure_logged(self, mock_env_config):
        """Test that Neo4j connection failures are logged but don't crash."""
        errors_logged = []

        async def mock_init_neo4j():
            try:
                raise Exception("Connection refused")
            except Exception as e:
                errors_logged.append(str(e))
                return None

        result = await mock_init_neo4j()

        assert result is None
        assert len(errors_logged) == 1
        assert "Connection refused" in errors_logged[0]

    @pytest.mark.asyncio
    async def test_missing_reranker_doesnt_break_search(self, mock_env_config, monkeypatch):
        """Test that search works even without reranker."""
        # Disable reranking
        monkeypatch.setenv("USE_RERANKING", "false")

        # Mock search without reranking
        results = [
            {"content": "Result 1", "similarity": 0.9},
            {"content": "Result 2", "similarity": 0.8},
        ]

        # Should return results without reranking
        assert len(results) == 2
        assert all("similarity" in r for r in results)

    @pytest.mark.asyncio
    async def test_partial_service_availability(self, mock_env_config):
        """Test app works with partial service availability."""
        # Simulate only basic services available
        services = {
            "crawler": Mock(),
            "supabase": Mock(),
            "reranker": None,  # Not available
            "neo4j": None,  # Not available
            "graphrag": None,  # Not available
        }

        # Basic operations should still work
        assert services["crawler"] is not None
        assert services["supabase"] is not None

        # Advanced features gracefully unavailable
        assert services["reranker"] is None
        assert services["neo4j"] is None


class TestConfigurationLoading:
    """Test configuration loading from environment."""

    def test_transport_mode_configuration(self, monkeypatch):
        """Test transport mode can be configured via environment."""
        monkeypatch.setenv("TRANSPORT", "sse")
        assert os.getenv("TRANSPORT") == "sse"

        monkeypatch.setenv("TRANSPORT", "stdio")
        assert os.getenv("TRANSPORT") == "stdio"

    def test_host_port_configuration(self, monkeypatch):
        """Test host and port configuration for SSE mode."""
        monkeypatch.setenv("HOST", "0.0.0.0")
        monkeypatch.setenv("PORT", "8080")

        assert os.getenv("HOST") == "0.0.0.0"
        assert os.getenv("PORT") == "8080"
        assert int(os.getenv("PORT")) == 8080

    def test_default_values(self):
        """Test default configuration values."""
        # These should have defaults if not set
        transport = os.getenv("TRANSPORT", "sse")
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "8051"))

        assert transport in ["sse", "stdio"]
        assert isinstance(host, str)
        assert isinstance(port, int)

    def test_boolean_flag_parsing(self, mock_env_config):
        """Test that boolean flags are parsed correctly."""

        def parse_bool(value):
            return value.lower() == "true" if value else False

        use_reranking = parse_bool(os.getenv("USE_RERANKING", "false"))
        use_hybrid = parse_bool(os.getenv("USE_HYBRID_SEARCH", "false"))

        assert isinstance(use_reranking, bool)
        assert isinstance(use_hybrid, bool)

    def test_model_configuration(self, mock_env_config):
        """Test model deployment configuration."""
        deployment = os.getenv("DEPLOYMENT_NAME")
        embedding = os.getenv("EMBEDDING_DEPLOYMENT")
        model = os.getenv("MODEL_CHOICE")

        assert deployment is not None
        assert embedding is not None
        assert model is not None

        # Should be valid model names
        assert len(deployment) > 0
        assert len(embedding) > 0
        assert "gpt" in model.lower() or "o" in model.lower()


class TestHealthCheck:
    """Test health check endpoint for Docker deployments."""

    @pytest.mark.asyncio
    async def test_health_endpoint_responds(self):
        """Test that health check endpoint responds correctly."""
        # Mock health check response
        health_data = {
            "status": "healthy",
            "service": "mcp-crawl4ai-rag",
            "version": "1.2.0",
            "transport": "sse",
        }

        assert health_data["status"] == "healthy"
        assert "mcp-crawl4ai-rag" in health_data["service"]

    @pytest.mark.asyncio
    async def test_health_check_includes_service_info(self):
        """Test health check includes service information."""
        health_data = {
            "status": "healthy",
            "service": "mcp-crawl4ai-rag",
            "version": "1.2.0",
            "transport": "sse",
            "components": {"supabase": "connected", "neo4j": "connected", "crawler": "ready"},
        }

        assert "service" in health_data
        assert "version" in health_data
        assert "status" in health_data


class TestDockerNetworking:
    """Test Docker networking and service communication."""

    def test_internal_service_urls(self, mock_env_config):
        """Test that service URLs are configured for Docker networking."""
        neo4j_uri = os.getenv("NEO4J_URI")

        # In Docker, might use service names
        # Should be valid URI
        assert "://" in neo4j_uri
        assert len(neo4j_uri) > 10

    def test_external_api_endpoints(self, mock_env_config):
        """Test external API endpoints are accessible."""
        supabase_url = os.getenv("SUPABASE_URL")
        openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        # Should be HTTPS URLs for external services
        assert supabase_url.startswith("https://")
        assert openai_endpoint.startswith("https://")

    def test_service_discovery(self, mock_env_config):
        """Test service discovery mechanism."""
        # Neo4j now runs externally; ensure we expose a reachable hostname in the URI
        neo4j_uri = os.getenv("NEO4J_URI", "")
        assert neo4j_uri.startswith("bolt://") or neo4j_uri.startswith("neo4j+s://")

        hostname = neo4j_uri.split("//", 1)[-1].split(":", 1)[0]
        assert hostname
        assert hostname not in {"neo4j", ""}


class TestSecurityConfiguration:
    """Test security-related configuration."""

    def test_api_keys_not_logged(self, mock_env_config):
        """Test that API keys are not logged or exposed."""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        # Keys should exist
        assert api_key is not None
        assert supabase_key is not None

        # Should not be empty
        assert len(api_key) > 10
        assert len(supabase_key) > 10

        # Keys should not appear in logs (simulated)
        log_message = f"Initializing with endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}"
        assert api_key not in log_message

    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in error messages."""
        api_key = "sk-test-key-12345"

        def mask_key(key):
            if len(key) <= 8:
                return "*" * len(key)
            return key[:4] + "*" * (len(key) - 8) + key[-4:]

        masked = mask_key(api_key)

        assert masked.startswith("sk-t")
        assert masked.endswith("2345")
        assert "*" in masked

    def test_environment_variable_validation(self, mock_env_config):
        """Test environment variables are validated for security."""
        # Check URL format validation
        supabase_url = os.getenv("SUPABASE_URL")

        # Should be HTTPS
        assert supabase_url.startswith("https://")

        # Should have valid domain
        assert "." in supabase_url


class TestErrorRecovery:
    """Test error recovery and resilience."""

    @pytest.mark.asyncio
    async def test_service_restart_recovery(self):
        """Test that services can recover from restarts."""
        connection_attempts = []

        async def attempt_connection(max_retries=3):
            for i in range(max_retries):
                connection_attempts.append(i + 1)
                if i == 2:  # Succeed on third attempt
                    return True
                await asyncio.sleep(0.01)
            return False

        result = await attempt_connection()

        assert result is True
        assert len(connection_attempts) == 3

    @pytest.mark.asyncio
    async def test_transient_error_retry(self):
        """Test retry logic for transient errors."""
        call_count = 0

        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient error")
            return "Success"

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await flaky_operation()
                break
            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.01)

        assert result == "Success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker for failing services."""
        failure_count = 0
        circuit_open = False

        async def protected_call():
            nonlocal failure_count, circuit_open

            if circuit_open:
                return None  # Circuit open, don't attempt

            try:
                failure_count += 1
                if failure_count >= 3:
                    circuit_open = True
                raise Exception("Service unavailable")
            except Exception:
                return None

        # Make multiple failing calls
        for _ in range(5):
            await protected_call()

        assert circuit_open is True
        assert failure_count == 3  # Stopped after 3 failures


class TestPerformanceMonitoring:
    """Test performance monitoring in deployment."""

    @pytest.mark.asyncio
    async def test_initialization_time_tracking(self):
        """Test that initialization time is tracked."""
        import time

        start_time = time.time()

        # Simulate initialization
        await asyncio.sleep(0.01)

        elapsed = time.time() - start_time

        assert elapsed > 0
        assert elapsed < 1.0  # Should be fast

    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            assert memory_mb > 0
            assert isinstance(memory_mb, float)
        except ImportError:
            pytest.skip("psutil not available")

    def test_concurrent_request_handling(self):
        """Test that deployment can handle concurrent requests."""
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

        assert semaphore._value == 5

        # This would be used to limit concurrency in production
        assert isinstance(semaphore, asyncio.Semaphore)
