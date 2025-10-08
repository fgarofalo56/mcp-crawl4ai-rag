"""Tests for new features: table extraction and adaptive crawling."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock


class TestTableExtraction:
    """Test crawl_with_table_extraction MCP tool."""
    
    @pytest.mark.asyncio
    async def test_table_extraction_basic(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test basic table extraction."""
        from src.crawl4ai_mcp import crawl_with_table_extraction
        
        # Setup mocks
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result with table content
        result = Mock()
        result.success = True
        result.markdown = "# Pricing\n\n| Plan | Price |\n|------|-------|\n| Basic | $10 |\n| Pro | $20 |"
        result.extracted_content = {
            'tables': [
                {
                    'headers': ['Plan', 'Price'],
                    'rows': [['Basic', '$10'], ['Pro', '$20']]
                }
            ]
        }
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Pricing table"):
                    response = await crawl_with_table_extraction(
                        mock_context,
                        "https://example.com/pricing",
                        table_score_threshold=5
                    )
        
        # Parse response
        data = json.loads(response)
        assert data["success"] is True
        assert "tables_extracted" in data["summary"]
        assert data["summary"]["table_score_threshold"] == 5
    
    @pytest.mark.asyncio
    async def test_table_extraction_no_tables(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test table extraction when no tables found."""
        from src.crawl4ai_mcp import crawl_with_table_extraction
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result without tables
        result = Mock()
        result.success = True
        result.markdown = "# Regular content\n\nNo tables here."
        result.extracted_content = {'tables': []}
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Content"):
                    response = await crawl_with_table_extraction(
                        mock_context,
                        "https://example.com",
                        table_score_threshold=7
                    )
        
        data = json.loads(response)
        assert data["success"] is True
        assert data["summary"]["tables_extracted"] == 0
    
    @pytest.mark.asyncio
    async def test_table_extraction_error(self, mock_context, mock_crawler, mock_env_vars):
        """Test table extraction with error."""
        from src.crawl4ai_mcp import crawl_with_table_extraction
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        
        # Mock failed result
        result = Mock()
        result.success = False
        mock_crawler.arun = AsyncMock(return_value=result)
        
        response = await crawl_with_table_extraction(
            mock_context,
            "https://example.com/pricing"
        )
        
        data = json.loads(response)
        assert data["success"] is False


class TestAdaptiveDeepCrawl:
    """Test adaptive_deep_crawl MCP tool."""
    
    @pytest.mark.asyncio
    async def test_adaptive_crawl_basic(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test basic adaptive crawling."""
        from src.crawl4ai_mcp import adaptive_deep_crawl
        
        # Setup mocks
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result
        result = Mock()
        result.success = True
        result.markdown = "# Authentication Guide\n\nOAuth2 is a protocol for authentication."
        result.crawled_pages = {
            "https://example.com/oauth": "OAuth2 authentication details"
        }
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Auth guide"):
                    response = await adaptive_deep_crawl(
                        mock_context,
                        "https://example.com/docs",
                        query="OAuth2 authentication",
                        max_pages=30,
                        strategy="best_first"
                    )
        
        # Parse response
        data = json.loads(response)
        assert data["success"] is True
        assert data["summary"]["query"] == "OAuth2 authentication"
        assert data["summary"]["strategy"] == "best_first"
        assert "avg_relevance" in data["summary"]
        assert "top_relevant_sources" in data
    
    @pytest.mark.asyncio
    async def test_adaptive_crawl_different_strategies(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test adaptive crawling with different strategies."""
        from src.crawl4ai_mcp import adaptive_deep_crawl
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        result = Mock()
        result.success = True
        result.markdown = "Content with API info"
        result.crawled_pages = {}
        mock_crawler.arun = AsyncMock(return_value=result)
        
        strategies = ["best_first", "bfs", "dfs"]
        
        for strategy in strategies:
            with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
                with patch('src.crawl4ai_mcp.update_source_info'):
                    with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Content"):
                        response = await adaptive_deep_crawl(
                            mock_context,
                            "https://example.com",
                            query="API documentation",
                            strategy=strategy
                        )
            
            data = json.loads(response)
            assert data["success"] is True
            assert data["summary"]["strategy"] == strategy
    
    @pytest.mark.asyncio
    async def test_adaptive_crawl_invalid_strategy(self, mock_context, mock_crawler, mock_env_vars):
        """Test adaptive crawling with invalid strategy."""
        from src.crawl4ai_mcp import adaptive_deep_crawl
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        
        response = await adaptive_deep_crawl(
            mock_context,
            "https://example.com",
            query="test",
            strategy="invalid_strategy"
        )
        
        data = json.loads(response)
        assert data["success"] is False
        assert "Invalid strategy" in data["error"]
    
    @pytest.mark.asyncio
    async def test_adaptive_crawl_relevance_scoring(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test relevance scoring in adaptive crawling."""
        from src.crawl4ai_mcp import adaptive_deep_crawl
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # Mock result with query-relevant content
        result = Mock()
        result.success = True
        result.markdown = """
        # API Authentication Guide
        
        OAuth2 authentication is the recommended method for API access.
        The authentication flow includes OAuth2 token exchange.
        """
        result.crawled_pages = {}
        mock_crawler.arun = AsyncMock(return_value=result)
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Auth guide"):
                    response = await adaptive_deep_crawl(
                        mock_context,
                        "https://example.com",
                        query="OAuth2 authentication API",
                        relevance_threshold=0.3
                    )
        
        data = json.loads(response)
        assert data["success"] is True
        # With 3 keyword matches in content, relevance should be > 0
        assert data["summary"]["avg_relevance"] > 0
    
    @pytest.mark.asyncio
    async def test_adaptive_crawl_error(self, mock_context, mock_crawler, mock_env_vars):
        """Test adaptive crawling with error."""
        from src.crawl4ai_mcp import adaptive_deep_crawl
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        
        # Mock failed result
        result = Mock()
        result.success = False
        mock_crawler.arun = AsyncMock(return_value=result)
        
        response = await adaptive_deep_crawl(
            mock_context,
            "https://example.com",
            query="test query"
        )
        
        data = json.loads(response)
        assert data["success"] is False


class TestNewFeaturesIntegration:
    """Integration tests for new features."""
    
    @pytest.mark.asyncio
    async def test_table_extraction_with_adaptive_crawl_workflow(self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars):
        """Test workflow combining table extraction and adaptive crawling."""
        from src.crawl4ai_mcp import crawl_with_table_extraction, adaptive_deep_crawl
        
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        
        # First, do adaptive crawl to find pricing page
        result1 = Mock()
        result1.success = True
        result1.markdown = "See our pricing page for details"
        result1.crawled_pages = {}
        
        # Then extract tables from pricing page
        result2 = Mock()
        result2.success = True
        result2.markdown = "| Plan | Price |"
        result2.extracted_content = {'tables': [{'headers': ['Plan', 'Price']}]}
        
        mock_crawler.arun = AsyncMock(side_effect=[result1, result2])
        
        with patch('src.crawl4ai_mcp.add_documents_to_supabase'):
            with patch('src.crawl4ai_mcp.update_source_info'):
                with patch('src.crawl4ai_mcp.extract_source_summary', return_value="Summary"):
                    # Step 1: Find pricing info
                    response1 = await adaptive_deep_crawl(
                        mock_context,
                        "https://example.com",
                        query="pricing plans",
                        max_pages=10
                    )
                    
                    # Step 2: Extract tables
                    response2 = await crawl_with_table_extraction(
                        mock_context,
                        "https://example.com/pricing"
                    )
        
        data1 = json.loads(response1)
        data2 = json.loads(response2)
        
        assert data1["success"] is True
        assert data2["success"] is True
        assert data1["summary"]["query"] == "pricing plans"
        assert "tables_extracted" in data2["summary"]
