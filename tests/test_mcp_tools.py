"""Tests for MCP tools (crawling, RAG, knowledge graph)."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
sys.path.insert(0, '/mnt/e/Repos/GitHub/mcp-crawl4ai-rag/knowledge_graphs')

# Import all MCP tools from crawl4ai_mcp
# We'll mock the actual implementations


class TestCrawlSinglePage:
    """Test crawl_single_page MCP tool."""
    
    @pytest.mark.asyncio
    async def test_crawl_single_page_success(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test successful single page crawl."""
        from src.crawl4ai_mcp import crawl_single_page
        
        # Setup mocks
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result
        result = Mock()
        result.success = True
        result.markdown = "# Test Page\n\nContent"
        result.links = {"internal": [], "external": []}
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                    response = await crawl_single_page(mock_context, "https://example.com")
        
        # Parse response
        data = json.loads(response)
        assert data["success"] is True
        assert data["url"] == "https://example.com"
        assert data["chunks_stored"] > 0
    
    @pytest.mark.asyncio
    async def test_crawl_single_page_failure(self, mock_context, mock_crawler, mock_env_vars):
        """Test single page crawl with failure."""
        from src.crawl4ai_mcp import crawl_single_page
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        
        # Mock failed result
        result = Mock()
        result.success = False
        result.error_message = "Failed to load page"
        mock_crawler.arun = AsyncMock(return_value=result)
        
        response = await crawl_single_page(mock_context, "https://example.com")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "error" in data
    
    @pytest.mark.asyncio
    async def test_crawl_single_page_with_code_extraction(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars, monkeypatch):
        """Test single page crawl with code example extraction."""
        from src.crawl4ai_mcp import crawl_single_page
        
        monkeypatch.setenv("USE_AGENTIC_RAG", "true")
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result with code
        result = Mock()
        result.success = True
        result.markdown = "```python\ndef test(): pass\n```"
        result.links = {"internal": [], "external": []}
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.add_code_examples_to_supabase'):
                with patch('src.crawl4ai_mcp.update_source_info'):
                    with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                        with patch('src.crawl4ai_mcp.extract_code_blocks', return_value=[{"code": "def test(): pass"}]):
                            with patch('src.crawl4ai_mcp.generate_code_example_summary', return_value="Test function"):
                                response = await crawl_single_page(mock_context, "https://example.com")
        
        data = json.loads(response)
        assert data["success"] is True


class TestSmartCrawlUrl:
    """Test smart_crawl_url MCP tool."""
    
    @pytest.mark.asyncio
    async def test_smart_crawl_sitemap(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test smart crawl with sitemap URL."""
        from src.crawl4ai_mcp import smart_crawl_url
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        with patch('src.crawl4ai_mcp.is_sitemap', return_value=True):
            with patch('src.crawl4ai_mcp.parse_sitemap', return_value=["https://example.com/page1"]):
                with patch('src.crawl4ai_mcp.crawl_batch', return_value=[{"url": "https://example.com/page1", "markdown": "Content"}]):
                    with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                        with patch('src.crawl4ai_mcp.update_source_info'):
                            with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                                response = await smart_crawl_url(mock_context, "https://example.com/sitemap.xml")
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["crawl_type"] == "sitemap"
    
    @pytest.mark.asyncio
    async def test_smart_crawl_txt_file(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test smart crawl with txt file."""
        from src.crawl4ai_mcp import smart_crawl_url
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        with patch('src.crawl4ai_mcp.is_txt', return_value=True):
            with patch('src.crawl4ai_mcp.crawl_markdown_file', return_value=[{"url": "https://example.com/llms.txt", "markdown": "Content"}]):
                with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                    with patch('src.crawl4ai_mcp.update_source_info'):
                        with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                            response = await smart_crawl_url(mock_context, "https://example.com/llms.txt")
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["crawl_type"] == "text_file"
    
    @pytest.mark.asyncio
    async def test_smart_crawl_webpage(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test smart crawl with regular webpage."""
        from src.crawl4ai_mcp import smart_crawl_url
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        with patch('src.crawl4ai_mcp.is_sitemap', return_value=False):
            with patch('src.crawl4ai_mcp.is_txt', return_value=False):
                with patch('src.crawl4ai_mcp.crawl_recursive_internal_links', return_value=[{"url": "https://example.com", "markdown": "Content"}]):
                    with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                        with patch('src.crawl4ai_mcp.update_source_info'):
                            with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                                response = await smart_crawl_url(mock_context, "https://example.com")
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["crawl_type"] == "webpage"


class TestCrawlWithStealthMode:
    """Test crawl_with_stealth_mode MCP tool."""
    
    @pytest.mark.asyncio
    async def test_stealth_crawl_success(self, mock_context, mock_supabase_client, mock_env_vars):
        """Test stealth mode crawl."""
        from src.crawl4ai_mcp import crawl_with_stealth_mode
        
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock stealth crawler
        with patch('src.crawl4ai_mcp.AsyncWebCrawler') as mock_crawler_class:
            mock_stealth_crawler = AsyncMock()
            mock_stealth_crawler.__aenter__ = AsyncMock(return_value=mock_stealth_crawler)
            mock_stealth_crawler.__aexit__ = AsyncMock()
            mock_crawler_class.return_value = mock_stealth_crawler
            
            with patch('src.crawl4ai_mcp.is_txt', return_value=False):
                with patch('src.crawl4ai_mcp.is_sitemap', return_value=False):
                    with patch('src.crawl4ai_mcp.crawl_recursive_internal_links', return_value=[{"url": "https://example.com", "markdown": "Content"}]):
                        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                            response = await crawl_with_stealth_mode(mock_context, "https://example.com")
        
        data = json.loads(response)
        assert data["success"] is True
        assert "stealth" in data["mode"]


class TestCrawlWithMultiUrlConfig:
    """Test crawl_with_multi_url_config MCP tool."""
    
    @pytest.mark.asyncio
    async def test_multi_url_crawl(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test multi-URL crawl with configuration."""
        from src.crawl4ai_mcp import crawl_with_multi_url_config
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        urls_json = '["https://docs.example.com", "https://news.example.com"]'
        
        with patch('src.crawl4ai_mcp.crawl_recursive_internal_links', return_value=[{"url": "https://example.com", "markdown": "Content"}]):
            with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                response = await crawl_with_multi_url_config(mock_context, urls_json)
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["urls_processed"] == 2
    
    @pytest.mark.asyncio
    async def test_multi_url_invalid_json(self, mock_context, mock_env_vars):
        """Test multi-URL crawl with invalid JSON."""
        from src.crawl4ai_mcp import crawl_with_multi_url_config
        
        response = await crawl_with_multi_url_config(mock_context, "invalid json")
        
        data = json.loads(response)
        assert "error" in data


class TestCrawlWithMemoryMonitoring:
    """Test crawl_with_memory_monitoring MCP tool."""
    
    @pytest.mark.asyncio
    async def test_memory_monitored_crawl(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test memory-monitored crawl."""
        from src.crawl4ai_mcp import crawl_with_memory_monitoring
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock psutil
        with patch('src.crawl4ai_mcp.psutil') as mock_psutil:
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(rss=100 * 1024 * 1024)  # 100 MB
            mock_psutil.Process.return_value = mock_process
            
            with patch('src.crawl4ai_mcp.is_txt', return_value=False):
                with patch('src.crawl4ai_mcp.is_sitemap', return_value=False):
                    with patch('src.crawl4ai_mcp.crawl_recursive_internal_links', return_value=[{"url": "https://example.com", "markdown": "Content"}]):
                        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                            response = await crawl_with_memory_monitoring(mock_context, "https://example.com")
        
        data = json.loads(response)
        assert data["success"] is True
        assert "memory_stats" in data


class TestGetAvailableSources:
    """Test get_available_sources MCP tool."""
    
    @pytest.mark.asyncio
    async def test_get_sources_success(self, mock_context, mock_supabase_client, mock_env_vars):
        """Test getting available sources."""
        from src.crawl4ai_mcp import get_available_sources
        
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock sources data
        mock_sources = [
            {"source_id": "example.com", "summary": "Test source", "total_words": 1000},
            {"source_id": "test.com", "summary": "Another source", "total_words": 500}
        ]
        mock_supabase_client.from_().select().order().execute.return_value = Mock(data=mock_sources)
        
        response = await get_available_sources(mock_context)
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["sources"]) == 2


class TestPerformRagQuery:
    """Test perform_rag_query MCP tool."""
    
    @pytest.mark.asyncio
    async def test_rag_query_vector_search(self, mock_context, mock_supabase_client, mock_env_vars, sample_search_results):
        """Test RAG query with vector search."""
        from src.crawl4ai_mcp import perform_rag_query
        
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        with patch('src.crawl4ai_mcp.search_documents', return_value=sample_search_results):
            response = await perform_rag_query(mock_context, "test query")
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["search_mode"] == "vector"
        assert len(data["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_rag_query_with_source_filter(self, mock_context, mock_supabase_client, mock_env_vars):
        """Test RAG query with source filter."""
        from src.crawl4ai_mcp import perform_rag_query
        
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        with patch('src.crawl4ai_mcp.search_documents', return_value=[]):
            response = await perform_rag_query(mock_context, "test query", source="example.com")
        
        data = json.loads(response)
        assert data["source_filter"] == "example.com"
    
    @pytest.mark.asyncio
    async def test_rag_query_hybrid_search(self, mock_context, mock_supabase_client, mock_env_vars, monkeypatch, sample_search_results):
        """Test RAG query with hybrid search enabled."""
        from src.crawl4ai_mcp import perform_rag_query
        
        monkeypatch.setenv("USE_HYBRID_SEARCH", "true")
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock both vector and keyword results
        mock_supabase_client.from_().select().ilike().limit().execute.return_value = Mock(data=[])
        
        with patch('src.crawl4ai_mcp.search_documents', return_value=sample_search_results):
            response = await perform_rag_query(mock_context, "test query")
        
        data = json.loads(response)
        assert data["search_mode"] == "hybrid"


class TestSearchCodeExamples:
    """Test search_code_examples MCP tool."""
    
    @pytest.mark.asyncio
    async def test_search_code_examples_disabled(self, mock_context, mock_env_vars):
        """Test code example search when disabled."""
        from src.crawl4ai_mcp import search_code_examples
        
        response = await search_code_examples(mock_context, "test query")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_search_code_examples_enabled(self, mock_context, mock_supabase_client, mock_env_vars, monkeypatch):
        """Test code example search when enabled."""
        from src.crawl4ai_mcp import search_code_examples
        
        monkeypatch.setenv("USE_AGENTIC_RAG", "true")
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        mock_results = [
            {"id": 1, "url": "https://example.com", "content": "def test(): pass", "summary": "Test function", "similarity": 0.9}
        ]
        
        with patch('src.utils.search_code_examples', return_value=mock_results):
            response = await search_code_examples(mock_context, "test function")
        
        data = json.loads(response)
        assert data["success"] is True
        assert len(data["results"]) == 1


class TestParseGithubRepository:
    """Test parse_github_repository MCP tool."""
    
    @pytest.mark.asyncio
    async def test_parse_repo_disabled(self, mock_context, mock_env_vars):
        """Test repository parsing when knowledge graph is disabled."""
        from src.crawl4ai_mcp import parse_github_repository
        
        response = await parse_github_repository(mock_context, "https://github.com/user/repo.git")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_parse_repo_invalid_url(self, mock_context, mock_env_vars, monkeypatch):
        """Test repository parsing with invalid URL."""
        from src.crawl4ai_mcp import parse_github_repository
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.repo_extractor = Mock()
        
        response = await parse_github_repository(mock_context, "not_a_url")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "error" in data
    
    @pytest.mark.asyncio
    async def test_parse_repo_success(self, mock_context, mock_repo_extractor, mock_env_vars, monkeypatch):
        """Test successful repository parsing."""
        from src.crawl4ai_mcp import parse_github_repository
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.repo_extractor = mock_repo_extractor
        
        # Mock Neo4j session and query results
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_record = {
            "repo_name": "test-repo",
            "files_count": 10,
            "classes_count": 5,
            "methods_count": 20,
            "functions_count": 15,
            "attributes_count": 10,
            "sample_modules": ["module1", "module2"]
        }
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_repo_extractor.driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_repo_extractor.driver.session.return_value.__aexit__ = AsyncMock()
        
        response = await parse_github_repository(mock_context, "https://github.com/user/test-repo.git")
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["repo_name"] == "test-repo"
        assert "statistics" in data


class TestCheckAiScriptHallucinations:
    """Test check_ai_script_hallucinations MCP tool."""
    
    @pytest.mark.asyncio
    async def test_hallucination_check_disabled(self, mock_context, mock_env_vars):
        """Test hallucination check when knowledge graph is disabled."""
        from src.crawl4ai_mcp import check_ai_script_hallucinations
        
        response = await check_ai_script_hallucinations(mock_context, "/path/to/script.py")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_hallucination_check_invalid_path(self, mock_context, mock_env_vars, monkeypatch):
        """Test hallucination check with invalid script path."""
        from src.crawl4ai_mcp import check_ai_script_hallucinations
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.knowledge_validator = Mock()
        
        response = await check_ai_script_hallucinations(mock_context, "/nonexistent/script.py")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "not found" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_hallucination_check_success(self, mock_context, mock_knowledge_validator, mock_env_vars, monkeypatch, tmp_path):
        """Test successful hallucination check."""
        from src.crawl4ai_mcp import check_ai_script_hallucinations
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.knowledge_validator = mock_knowledge_validator
        
        # Create temporary Python file
        script_file = tmp_path / "test_script.py"
        script_file.write_text("def test(): pass")
        
        # Mock analysis components
        with patch('src.crawl4ai_mcp.AIScriptAnalyzer') as mock_analyzer_class:
            with patch('src.crawl4ai_mcp.HallucinationReporter') as mock_reporter_class:
                mock_analyzer = Mock()
                mock_analysis_result = Mock()
                mock_analysis_result.errors = []
                mock_analyzer.analyze_script.return_value = mock_analysis_result
                mock_analyzer_class.return_value = mock_analyzer
                
                mock_reporter = Mock()
                mock_report = {
                    "validation_summary": {
                        "total_validations": 10,
                        "valid_count": 9,
                        "invalid_count": 1,
                        "uncertain_count": 0,
                        "not_found_count": 0,
                        "hallucination_rate": 0.1
                    },
                    "hallucinations_detected": [],
                    "recommendations": [],
                    "analysis_metadata": {
                        "total_imports": 5,
                        "total_classes": 2,
                        "total_methods": 10,
                        "total_attributes": 5,
                        "total_functions": 3
                    },
                    "libraries_analyzed": ["test"]
                }
                mock_reporter.generate_comprehensive_report.return_value = mock_report
                mock_reporter_class.return_value = mock_reporter
                
                # Mock validation result
                mock_validation_result = Mock()
                mock_validation_result.overall_confidence = 0.9
                mock_knowledge_validator.validate_script.return_value = mock_validation_result
                
                response = await check_ai_script_hallucinations(mock_context, str(script_file))
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["overall_confidence"] == 0.9


class TestQueryKnowledgeGraph:
    """Test query_knowledge_graph MCP tool."""
    
    @pytest.mark.asyncio
    async def test_query_kg_disabled(self, mock_context, mock_env_vars):
        """Test knowledge graph query when disabled."""
        from src.crawl4ai_mcp import query_knowledge_graph
        
        response = await query_knowledge_graph(mock_context, "repos")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_query_kg_repos_command(self, mock_context, mock_repo_extractor, mock_env_vars, monkeypatch):
        """Test knowledge graph repos command."""
        from src.crawl4ai_mcp import query_knowledge_graph
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.repo_extractor = mock_repo_extractor
        
        # Mock Neo4j session
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        
        # Create async iterator for results
        async def async_iter_repos():
            yield {"name": "repo1"}
            yield {"name": "repo2"}
        
        mock_result.__aiter__ = lambda x: async_iter_repos()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_repo_extractor.driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_repo_extractor.driver.session.return_value.__aexit__ = AsyncMock()
        
        response = await query_knowledge_graph(mock_context, "repos")
        
        data = json.loads(response)
        assert data["success"] is True
        assert "repositories" in data["data"]
    
    @pytest.mark.asyncio
    async def test_query_kg_invalid_command(self, mock_context, mock_repo_extractor, mock_env_vars, monkeypatch):
        """Test knowledge graph with invalid command."""
        from src.crawl4ai_mcp import query_knowledge_graph
        
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        mock_context.request_context.lifespan_context.repo_extractor = mock_repo_extractor
        
        response = await query_knowledge_graph(mock_context, "invalid_command")
        
        data = json.loads(response)
        assert data["success"] is False
        assert "Unknown command" in data["error"]


class TestHelperFunctions:
    """Test helper functions in crawl4ai_mcp."""
    
    def test_is_sitemap_true(self):
        """Test sitemap detection for sitemap URLs."""
        from src.crawl4ai_mcp import is_sitemap
        
        assert is_sitemap("https://example.com/sitemap.xml") is True
        assert is_sitemap("https://example.com/path/to/sitemap.xml") is True
    
    def test_is_sitemap_false(self):
        """Test sitemap detection for non-sitemap URLs."""
        from src.crawl4ai_mcp import is_sitemap
        
        assert is_sitemap("https://example.com") is False
        assert is_sitemap("https://example.com/page.html") is False
    
    def test_is_txt_true(self):
        """Test txt file detection."""
        from src.crawl4ai_mcp import is_txt
        
        assert is_txt("https://example.com/llms.txt") is True
        assert is_txt("https://example.com/file.txt") is True
    
    def test_is_txt_false(self):
        """Test txt file detection for non-txt URLs."""
        from src.crawl4ai_mcp import is_txt
        
        assert is_txt("https://example.com") is False
        assert is_txt("https://example.com/page.html") is False
    
    def test_smart_chunk_markdown(self):
        """Test smart markdown chunking."""
        from src.crawl4ai_mcp import smart_chunk_markdown
        
        text = "x" * 10000
        chunks = smart_chunk_markdown(text, chunk_size=5000)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 5000 * 1.5 for chunk in chunks)  # Allow some overflow
    
    def test_smart_chunk_markdown_with_code_blocks(self):
        """Test smart chunking respects code blocks."""
        from src.crawl4ai_mcp import smart_chunk_markdown
        
        text = "Before\n\n```python\n" + ("x" * 1000) + "\n```\n\nAfter"
        chunks = smart_chunk_markdown(text, chunk_size=500)
        
        # Should try to keep code block together
        assert len(chunks) > 0
    
    def test_extract_section_info(self):
        """Test section info extraction from markdown."""
        from src.crawl4ai_mcp import extract_section_info
        
        chunk = "# Header 1\n\n## Header 2\n\nContent here"
        info = extract_section_info(chunk)
        
        assert "Header 1" in info["headers"]
        assert "Header 2" in info["headers"]
        assert info["char_count"] > 0
        assert info["word_count"] > 0
    
    def test_rerank_results(self):
        """Test result reranking."""
        from src.crawl4ai_mcp import rerank_results
        
        # Create mock cross-encoder
        mock_model = Mock()
        mock_model.predict.return_value = [0.9, 0.7, 0.8]
        
        results = [
            {"content": "text 1"},
            {"content": "text 2"},
            {"content": "text 3"}
        ]
        
        reranked = rerank_results(mock_model, "query", results)
        
        assert len(reranked) == 3
        assert reranked[0]["rerank_score"] == 0.9
    
    def test_rerank_results_no_model(self):
        """Test reranking with no model returns original results."""
        from src.crawl4ai_mcp import rerank_results
        
        results = [{"content": "text"}]
        reranked = rerank_results(None, "query", results)
        
        assert reranked == results
    
    def test_validate_neo4j_connection(self, mock_env_vars):
        """Test Neo4j connection validation."""
        from src.crawl4ai_mcp import validate_neo4j_connection
        
        assert validate_neo4j_connection() is True
    
    def test_validate_neo4j_connection_missing(self, monkeypatch):
        """Test Neo4j connection validation with missing vars."""
        from src.crawl4ai_mcp import validate_neo4j_connection
        
        monkeypatch.delenv("NEO4J_URI", raising=False)
        
        assert validate_neo4j_connection() is False
    
    def test_validate_script_path_valid(self, tmp_path):
        """Test script path validation with valid path."""
        from src.crawl4ai_mcp import validate_script_path
        
        script_file = tmp_path / "test.py"
        script_file.write_text("print('hello')")
        
        result = validate_script_path(str(script_file))
        assert result["valid"] is True
    
    def test_validate_script_path_invalid(self):
        """Test script path validation with invalid path."""
        from src.crawl4ai_mcp import validate_script_path
        
        result = validate_script_path("/nonexistent/script.py")
        assert result["valid"] is False
        assert "not found" in result["error"].lower()
    
    def test_validate_script_path_not_python(self, tmp_path):
        """Test script path validation with non-Python file."""
        from src.crawl4ai_mcp import validate_script_path
        
        script_file = tmp_path / "test.txt"
        script_file.write_text("text")
        
        result = validate_script_path(str(script_file))
        assert result["valid"] is False
        assert "Python" in result["error"]
    
    def test_validate_github_url_valid(self):
        """Test GitHub URL validation with valid URLs."""
        from src.crawl4ai_mcp import validate_github_url
        
        result = validate_github_url("https://github.com/user/repo.git")
        assert result["valid"] is True
        assert result["repo_name"] == "repo"
    
    def test_validate_github_url_invalid(self):
        """Test GitHub URL validation with invalid URLs."""
        from src.crawl4ai_mcp import validate_github_url
        
        result = validate_github_url("not_a_url")
        assert result["valid"] is False
