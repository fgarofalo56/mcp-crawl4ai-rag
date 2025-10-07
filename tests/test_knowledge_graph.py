"""Tests for knowledge graph modules (validation, parsing, analysis)."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
sys.path.insert(0, '/mnt/e/Repos/GitHub/mcp-crawl4ai-rag/knowledge_graphs')


class TestKnowledgeGraphValidator:
    """Test KnowledgeGraphValidator functionality."""
    
    @pytest.mark.asyncio
    async def test_validator_initialization(self, mock_neo4j_driver):
        """Test knowledge graph validator initialization."""
        from knowledge_graph_validator import KnowledgeGraphValidator
        
        validator = KnowledgeGraphValidator(
            "bolt://localhost:7687",
            "neo4j",
            "password"
        )
        
        assert validator is not None
    
    @pytest.mark.asyncio
    async def test_validator_initialize_and_close(self, mock_neo4j_driver):
        """Test validator initialization and cleanup."""
        from knowledge_graph_validator import KnowledgeGraphValidator
        
        with patch('knowledge_graph_validator.GraphDatabase'):
            validator = KnowledgeGraphValidator(
                "bolt://localhost:7687",
                "neo4j",
                "password"
            )
            
            await validator.initialize()
            await validator.close()


class TestDirectNeo4jExtractor:
    """Test DirectNeo4jExtractor functionality."""
    
    @pytest.mark.asyncio
    async def test_extractor_initialization(self):
        """Test repository extractor initialization."""
        from parse_repo_into_neo4j import DirectNeo4jExtractor
        
        extractor = DirectNeo4jExtractor(
            "bolt://localhost:7687",
            "neo4j",
            "password"
        )
        
        assert extractor is not None
    
    @pytest.mark.asyncio
    async def test_extractor_analyze_repository(self):
        """Test repository analysis workflow."""
        from parse_repo_into_neo4j import DirectNeo4jExtractor
        
        with patch('parse_repo_into_neo4j.GraphDatabase'):
            with patch('parse_repo_into_neo4j.Repo') as mock_repo:
                # Mock git clone
                mock_repo.clone_from.return_value = Mock()
                
                extractor = DirectNeo4jExtractor(
                    "bolt://localhost:7687",
                    "neo4j",
                    "password"
                )
                extractor.driver = AsyncMock()
                
                # This would normally clone and analyze - we're just testing structure
                # Full integration test would require actual Neo4j
                assert extractor is not None


class TestAIScriptAnalyzer:
    """Test AIScriptAnalyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test script analyzer initialization."""
        from ai_script_analyzer import AIScriptAnalyzer
        
        analyzer = AIScriptAnalyzer()
        assert analyzer is not None
    
    def test_analyze_simple_script(self, tmp_path):
        """Test analyzing a simple Python script."""
        from ai_script_analyzer import AIScriptAnalyzer
        
        # Create a simple test script
        script_file = tmp_path / "test_script.py"
        script_file.write_text("""
import os

def hello():
    return "world"

class TestClass:
    def __init__(self):
        self.value = 42
""")
        
        analyzer = AIScriptAnalyzer()
        result = analyzer.analyze_script(str(script_file))
        
        assert result is not None
        # Script should have imports, functions, and classes
        assert len(result.imports) > 0
        assert len(result.functions) > 0 or len(result.classes) > 0
    
    def test_analyze_script_with_syntax_error(self, tmp_path):
        """Test analyzing script with syntax errors."""
        from ai_script_analyzer import AIScriptAnalyzer
        
        script_file = tmp_path / "bad_script.py"
        script_file.write_text("def incomplete(:\n    pass")
        
        analyzer = AIScriptAnalyzer()
        result = analyzer.analyze_script(str(script_file))
        
        # Should handle syntax errors gracefully
        assert result is not None
        assert len(result.errors) > 0


class TestHallucinationReporter:
    """Test HallucinationReporter functionality."""
    
    def test_reporter_initialization(self):
        """Test hallucination reporter initialization."""
        from hallucination_reporter import HallucinationReporter
        
        reporter = HallucinationReporter()
        assert reporter is not None
    
    def test_generate_comprehensive_report(self):
        """Test comprehensive report generation."""
        from hallucination_reporter import HallucinationReporter
        
        # Mock validation result
        validation_result = Mock()
        validation_result.overall_confidence = 0.85
        validation_result.validations = []
        validation_result.hallucinations = []
        validation_result.warnings = []
        
        reporter = HallucinationReporter()
        report = reporter.generate_comprehensive_report(validation_result)
        
        assert report is not None
        assert "validation_summary" in report
        assert "hallucinations_detected" in report
        assert "recommendations" in report


class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_format_neo4j_error_authentication(self):
        """Test Neo4j error formatting for authentication errors."""
        from src.crawl4ai_mcp import format_neo4j_error
        
        error = Exception("Authentication failed")
        message = format_neo4j_error(error)
        
        assert "authentication" in message.lower()
    
    def test_format_neo4j_error_connection(self):
        """Test Neo4j error formatting for connection errors."""
        from src.crawl4ai_mcp import format_neo4j_error
        
        error = Exception("Connection refused")
        message = format_neo4j_error(error)
        
        assert "connect" in message.lower()
    
    def test_format_neo4j_error_database(self):
        """Test Neo4j error formatting for database errors."""
        from src.crawl4ai_mcp import format_neo4j_error
        
        error = Exception("Database not found")
        message = format_neo4j_error(error)
        
        assert "database" in message.lower()
    
    def test_format_neo4j_error_generic(self):
        """Test Neo4j error formatting for generic errors."""
        from src.crawl4ai_mcp import format_neo4j_error
        
        error = Exception("Unknown error occurred")
        message = format_neo4j_error(error)
        
        assert "Neo4j error" in message


class TestAsyncCrawlingHelpers:
    """Test async crawling helper functions."""
    
    @pytest.mark.asyncio
    async def test_crawl_markdown_file(self, mock_crawler):
        """Test crawling a markdown/text file."""
        from src.crawl4ai_mcp import crawl_markdown_file
        
        result = Mock()
        result.success = True
        result.markdown = "Test content"
        mock_crawler.arun = AsyncMock(return_value=result)
        
        results = await crawl_markdown_file(mock_crawler, "https://example.com/file.txt")
        
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com/file.txt"
        assert results[0]["markdown"] == "Test content"
    
    @pytest.mark.asyncio
    async def test_crawl_markdown_file_failure(self, mock_crawler):
        """Test crawling a file that fails."""
        from src.crawl4ai_mcp import crawl_markdown_file
        
        result = Mock()
        result.success = False
        result.error_message = "Failed"
        mock_crawler.arun = AsyncMock(return_value=result)
        
        results = await crawl_markdown_file(mock_crawler, "https://example.com/file.txt")
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_crawl_batch(self, mock_crawler):
        """Test batch crawling multiple URLs."""
        from src.crawl4ai_mcp import crawl_batch
        
        # Mock successful results
        results = [Mock(success=True, markdown=f"Content {i}", url=f"https://example.com/page{i}") 
                  for i in range(3)]
        mock_crawler.arun_many = AsyncMock(return_value=results)
        
        urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        crawled = await crawl_batch(mock_crawler, urls)
        
        assert len(crawled) == 3
        assert all("url" in item and "markdown" in item for item in crawled)
    
    @pytest.mark.asyncio
    async def test_crawl_recursive_internal_links(self, mock_crawler):
        """Test recursive crawling of internal links."""
        from src.crawl4ai_mcp import crawl_recursive_internal_links
        
        # Mock results with internal links
        result1 = Mock(
            success=True,
            markdown="Content 1",
            url="https://example.com/page1",
            links={"internal": [{"href": "https://example.com/page2"}], "external": []}
        )
        result2 = Mock(
            success=True,
            markdown="Content 2",
            url="https://example.com/page2",
            links={"internal": [], "external": []}
        )
        
        mock_crawler.arun_many = AsyncMock(side_effect=[[result1], [result2]])
        
        results = await crawl_recursive_internal_links(
            mock_crawler,
            ["https://example.com/page1"],
            max_depth=2
        )
        
        assert len(results) >= 1
        assert all("url" in item and "markdown" in item for item in results)


class TestSitemapParsing:
    """Test sitemap parsing functionality."""
    
    def test_parse_sitemap_success(self):
        """Test successful sitemap parsing."""
        from src.crawl4ai_mcp import parse_sitemap
        
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
    </url>
</urlset>"""
        
        with patch('src.crawl4ai_mcp.requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=sitemap_xml.encode())
            
            urls = parse_sitemap("https://example.com/sitemap.xml")
            
            assert len(urls) == 2
            assert "https://example.com/page1" in urls
            assert "https://example.com/page2" in urls
    
    def test_parse_sitemap_error(self):
        """Test sitemap parsing with HTTP error."""
        from src.crawl4ai_mcp import parse_sitemap
        
        with patch('src.crawl4ai_mcp.requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=404)
            
            urls = parse_sitemap("https://example.com/sitemap.xml")
            
            assert urls == []
    
    def test_parse_sitemap_invalid_xml(self):
        """Test sitemap parsing with invalid XML."""
        from src.crawl4ai_mcp import parse_sitemap
        
        with patch('src.crawl4ai_mcp.requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=b"invalid xml")
            
            urls = parse_sitemap("https://example.com/sitemap.xml")
            
            assert urls == []


class TestProcessCodeExample:
    """Test parallel code example processing."""
    
    def test_process_code_example(self, mock_openai_client, mock_env_vars):
        """Test processing single code example."""
        from src.crawl4ai_mcp import process_code_example
        
        with patch('src.utils.client', mock_openai_client):
            args = ("def test(): pass", "Before context", "After context")
            summary = process_code_example(args)
            
            assert summary is not None
            assert isinstance(summary, str)
