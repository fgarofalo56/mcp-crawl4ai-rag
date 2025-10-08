"""
MCP server for web crawling with Crawl4AI.

This server provides tools to crawl websites using Crawl4AI, automatically detecting
the appropriate crawl method based on URL type (sitemap, txt file, or regular webpage).
Also includes AI hallucination detection and repository parsing tools using Neo4j knowledge graphs.
"""

# Suppress known deprecation warnings from dependencies BEFORE imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="supabase.*")
warnings.filterwarnings("ignore", message=".*class-based `config` is deprecated.*")
warnings.filterwarnings("ignore", message=".*The `gotrue` package is deprecated.*")

from fastmcp import FastMCP, Context
from sentence_transformers import CrossEncoder
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urldefrag
from xml.etree import ElementTree
from dotenv import load_dotenv
from supabase import Client
from pathlib import Path
import requests
import asyncio
import json
import os
import re
import concurrent.futures
import sys

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    MemoryAdaptiveDispatcher,
)

# Add knowledge_graphs folder to path for importing knowledge graph modules
knowledge_graphs_path = Path(__file__).resolve().parent.parent / "knowledge_graphs"
sys.path.append(str(knowledge_graphs_path))

from .utils import (
    get_supabase_client,
    add_documents_to_supabase,
    search_documents,
    extract_code_blocks,
    generate_code_example_summary,
    add_code_examples_to_supabase,
    update_source_info,
    extract_source_summary,
    search_code_examples,
)

# Import knowledge graph modules (code repository graph)
from knowledge_graph_validator import KnowledgeGraphValidator
from parse_repo_into_neo4j import DirectNeo4jExtractor
from ai_script_analyzer import AIScriptAnalyzer
from hallucination_reporter import HallucinationReporter

# Import document graph modules (GraphRAG for web content)
from document_graph_validator import DocumentGraphValidator
from document_entity_extractor import DocumentEntityExtractor
from document_graph_queries import DocumentGraphQueries

from dotenv import load_dotenv

load_dotenv()


# Load environment variables from the project root .env file
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / ".env"

# Force override of existing environment variables
load_dotenv(dotenv_path, override=True)


# Helper functions for Neo4j validation and error handling
def validate_neo4j_connection() -> bool:
    """Check if Neo4j environment variables are configured."""
    return all(
        [os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")]
    )


def format_neo4j_error(error: Exception) -> str:
    """Format Neo4j connection errors for user-friendly messages."""
    error_str = str(error).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str or "timeout" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "database" in error_str:
        return "Neo4j database error. Check if the database exists and is accessible."
    else:
        return f"Neo4j error: {str(error)}"


def validate_script_path(script_path: str) -> Dict[str, Any]:
    """Validate script path and return error info if invalid."""
    if not script_path or not isinstance(script_path, str):
        return {"valid": False, "error": "Script path is required"}

    if not os.path.exists(script_path):
        return {"valid": False, "error": f"Script not found: {script_path}"}

    if not script_path.endswith(".py"):
        return {"valid": False, "error": "Only Python (.py) files are supported"}

    try:
        # Check if file is readable
        with open(script_path, "r", encoding="utf-8") as f:
            f.read(1)  # Read first character to test
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": f"Cannot read script file: {str(e)}"}


def validate_github_url(repo_url: str) -> Dict[str, Any]:
    """Validate GitHub repository URL."""
    if not repo_url or not isinstance(repo_url, str):
        return {"valid": False, "error": "Repository URL is required"}

    repo_url = repo_url.strip()

    # Basic GitHub URL validation
    if not ("github.com" in repo_url.lower() or repo_url.endswith(".git")):
        return {"valid": False, "error": "Please provide a valid GitHub repository URL"}

    # Check URL format
    if not (repo_url.startswith("https://") or repo_url.startswith("git@")):
        return {
            "valid": False,
            "error": "Repository URL must start with https:// or git@",
        }

    return {"valid": True, "repo_name": repo_url.split("/")[-1].replace(".git", "")}


# Create a dataclass for our application context
@dataclass
class Crawl4AIContext:
    """Context for the Crawl4AI MCP server."""

    crawler: AsyncWebCrawler
    supabase_client: Client
    reranking_model: Optional[CrossEncoder] = None
    knowledge_validator: Optional[Any] = None  # KnowledgeGraphValidator when available
    repo_extractor: Optional[Any] = None  # DirectNeo4jExtractor when available
    # GraphRAG components (document knowledge graph)
    document_graph_validator: Optional[Any] = None  # DocumentGraphValidator when available
    document_entity_extractor: Optional[Any] = None  # DocumentEntityExtractor when available
    document_graph_queries: Optional[Any] = None  # DocumentGraphQueries when available


@asynccontextmanager
async def crawl4ai_lifespan(server: FastMCP) -> AsyncIterator[Crawl4AIContext]:
    """
    Manages the Crawl4AI client lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        Crawl4AIContext: The context containing the Crawl4AI crawler and Supabase client
    """
    # Create browser configuration
    browser_config = BrowserConfig(headless=True, verbose=False)

    # Initialize the crawler
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.__aenter__()

    # Initialize Supabase client
    supabase_client = get_supabase_client()

    # Initialize cross-encoder model for reranking if enabled
    reranking_model = None
    if os.getenv("USE_RERANKING", "false") == "true":
        try:
            reranking_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            print(f"Failed to load reranking model: {e}")
            reranking_model = None

    # Initialize Neo4j components if configured and enabled
    knowledge_validator = None
    repo_extractor = None

    # Check if knowledge graph functionality is enabled
    knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"

    if knowledge_graph_enabled:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        if neo4j_uri and neo4j_user and neo4j_password:
            try:
                print("Initializing knowledge graph components...")

                # Initialize knowledge graph validator
                knowledge_validator = KnowledgeGraphValidator(
                    neo4j_uri, neo4j_user, neo4j_password
                )
                await knowledge_validator.initialize()
                print("✓ Knowledge graph validator initialized")

                # Initialize repository extractor
                repo_extractor = DirectNeo4jExtractor(
                    neo4j_uri, neo4j_user, neo4j_password
                )
                await repo_extractor.initialize()
                print("✓ Repository extractor initialized")

            except Exception as e:
                print(f"Failed to initialize Neo4j components: {format_neo4j_error(e)}")
                knowledge_validator = None
                repo_extractor = None

    # Initialize GraphRAG components (document knowledge graph)
    document_graph_validator = None
    document_entity_extractor = None
    document_graph_queries = None

    graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"

    if graphrag_enabled:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")

        if neo4j_uri and neo4j_user and neo4j_password:
            try:
                print("Initializing GraphRAG components...")

                # Initialize document graph validator (schema management)
                document_graph_validator = DocumentGraphValidator(
                    neo4j_uri, neo4j_user, neo4j_password
                )
                await document_graph_validator.initialize()
                print("✓ Document graph validator initialized")

                # Initialize document graph queries
                document_graph_queries = DocumentGraphQueries(
                    neo4j_uri, neo4j_user, neo4j_password
                )
                await document_graph_queries.initialize()
                print("✓ Document graph queries initialized")

                # Initialize entity extractor (requires OpenAI)
                if azure_openai_endpoint and azure_openai_key:
                    document_entity_extractor = DocumentEntityExtractor(
                        azure_openai_endpoint=azure_openai_endpoint,
                        azure_openai_key=azure_openai_key,
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    )
                    print("✓ Document entity extractor initialized (Azure OpenAI)")
                elif openai_api_key:
                    document_entity_extractor = DocumentEntityExtractor(
                        openai_api_key=openai_api_key,
                        model="gpt-4o-mini"
                    )
                    print("✓ Document entity extractor initialized (OpenAI)")
                else:
                    print("⚠ OpenAI API key not configured - entity extraction will be unavailable")

            except Exception as e:
                print(f"Failed to initialize GraphRAG components: {e}")
                document_graph_validator = None
                document_entity_extractor = None
                document_graph_queries = None
        else:
            print(
                "Neo4j credentials not configured - GraphRAG tools will be unavailable"
            )
    else:
        print(
            "GraphRAG functionality disabled - set USE_GRAPHRAG=true to enable"
        )

    try:
        yield Crawl4AIContext(
            crawler=crawler,
            supabase_client=supabase_client,
            reranking_model=reranking_model,
            knowledge_validator=knowledge_validator,
            repo_extractor=repo_extractor,
            document_graph_validator=document_graph_validator,
            document_entity_extractor=document_entity_extractor,
            document_graph_queries=document_graph_queries,
        )
    finally:
        # Clean up all components
        await crawler.__aexit__(None, None, None)
        if knowledge_validator:
            try:
                await knowledge_validator.close()
                print("✓ Knowledge graph validator closed")
            except Exception as e:
                print(f"Error closing knowledge validator: {e}")
        if repo_extractor:
            try:
                await repo_extractor.close()
                print("✓ Repository extractor closed")
            except Exception as e:
                print(f"Error closing repository extractor: {e}")
        # Clean up GraphRAG components
        if document_graph_validator:
            try:
                await document_graph_validator.close()
                print("✓ Document graph validator closed")
            except Exception as e:
                print(f"Error closing document graph validator: {e}")
        if document_graph_queries:
            try:
                await document_graph_queries.close()
                print("✓ Document graph queries closed")
            except Exception as e:
                print(f"Error closing document graph queries: {e}")


# Initialize FastMCP server
mcp = FastMCP(
    name="mcp-crawl4ai-rag",
    lifespan=crawl4ai_lifespan,
)


def rerank_results(
    model: CrossEncoder,
    query: str,
    results: List[Dict[str, Any]],
    content_key: str = "content",
) -> List[Dict[str, Any]]:
    """
    Rerank search results using a cross-encoder model.

    Args:
        model: The cross-encoder model to use for reranking
        query: The search query
        results: List of search results
        content_key: The key in each result dict that contains the text content

    Returns:
        Reranked list of results
    """
    if not model or not results:
        return results

    try:
        # Extract content from results
        texts = [result.get(content_key, "") for result in results]

        # Create pairs of [query, document] for the cross-encoder
        pairs = [[query, text] for text in texts]

        # Get relevance scores from the cross-encoder
        scores = model.predict(pairs)

        # Add scores to results and sort by score (descending)
        for i, result in enumerate(results):
            result["rerank_score"] = float(scores[i])

        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x.get("rerank_score", 0), reverse=True)

        return reranked
    except Exception as e:
        print(f"Error during reranking: {e}")
        return results


def is_sitemap(url: str) -> bool:
    """
    Check if a URL is a sitemap.

    Args:
        url: URL to check

    Returns:
        True if the URL is a sitemap, False otherwise
    """
    return url.endswith("sitemap.xml") or "sitemap" in urlparse(url).path


def is_txt(url: str) -> bool:
    """
    Check if a URL is a text file.

    Args:
        url: URL to check

    Returns:
        True if the URL is a text file, False otherwise
    """
    return url.endswith(".txt")


def parse_sitemap(sitemap_url: str) -> List[str]:
    """
    Parse a sitemap and extract URLs.

    Args:
        sitemap_url: URL of the sitemap

    Returns:
        List of URLs found in the sitemap
    """
    resp = requests.get(sitemap_url)
    urls = []

    if resp.status_code == 200:
        try:
            tree = ElementTree.fromstring(resp.content)
            urls = [loc.text for loc in tree.findall(".//{*}loc")]
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")

    return urls


def smart_chunk_markdown(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks, respecting code blocks and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind("```")
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif "\n\n" in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind("\n\n")
            if (
                last_break > chunk_size * 0.3
            ):  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif ". " in chunk:
            # Find the last sentence break
            last_period = chunk.rfind(". ")
            if (
                last_period > chunk_size * 0.3
            ):  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = end

    return chunks


def extract_section_info(chunk: str) -> Dict[str, Any]:
    """
    Extracts headers and stats from a chunk.

    Args:
        chunk: Markdown chunk

    Returns:
        Dictionary with headers and stats
    """
    headers = re.findall(r"^(#+)\s+(.+)$", chunk, re.MULTILINE)
    header_str = "; ".join([f"{h[0]} {h[1]}" for h in headers]) if headers else ""

    return {
        "headers": header_str,
        "char_count": len(chunk),
        "word_count": len(chunk.split()),
    }


def process_code_example(args):
    """
    Process a single code example to generate its summary.
    This function is designed to be used with concurrent.futures.

    Args:
        args: Tuple containing (code, context_before, context_after)

    Returns:
        The generated summary
    """
    code, context_before, context_after = args
    return generate_code_example_summary(code, context_before, context_after)


@mcp.tool()
async def crawl_single_page(ctx: Context, url: str) -> str:
    """
    Crawl a single web page and store its content in Supabase.

    This tool is ideal for quickly retrieving content from a specific URL without following links.
    The content is stored in Supabase for later retrieval and querying.

    Args:
        ctx: The MCP server provided context
        url: URL of the web page to crawl

    Returns:
        Summary of the crawling operation and storage in Supabase
    """
    try:
        # Get the crawler from the context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Configure the crawl
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)

        # Crawl the page
        result = await crawler.arun(url=url, config=run_config)

        if result.success and result.markdown:
            # Extract source_id
            parsed_url = urlparse(url)
            source_id = parsed_url.netloc or parsed_url.path

            # Chunk the content
            chunks = smart_chunk_markdown(result.markdown)

            # Prepare data for Supabase
            urls = []
            chunk_numbers = []
            contents = []
            metadatas = []
            total_word_count = 0

            for i, chunk in enumerate(chunks):
                urls.append(url)
                chunk_numbers.append(i)
                contents.append(chunk)

                # Extract metadata
                meta = extract_section_info(chunk)
                meta["chunk_index"] = i
                meta["url"] = url
                meta["source"] = source_id
                meta["crawl_time"] = str(asyncio.current_task().get_coro().__name__)
                metadatas.append(meta)

                # Accumulate word count
                total_word_count += meta.get("word_count", 0)

            # Create url_to_full_document mapping
            url_to_full_document = {url: result.markdown}

            # Update source information FIRST (before inserting documents)
            source_summary = extract_source_summary(
                source_id, result.markdown[:5000]
            )  # Use first 5000 chars for summary
            update_source_info(
                supabase_client, source_id, source_summary, total_word_count
            )

            # Add documentation chunks to Supabase (AFTER source exists)
            add_documents_to_supabase(
                supabase_client,
                urls,
                chunk_numbers,
                contents,
                metadatas,
                url_to_full_document,
            )

            # Extract and process code examples only if enabled
            extract_code_examples = os.getenv("USE_AGENTIC_RAG", "false") == "true"
            if extract_code_examples:
                code_blocks = extract_code_blocks(result.markdown)
                if code_blocks:
                    code_urls = []
                    code_chunk_numbers = []
                    code_examples = []
                    code_summaries = []
                    code_metadatas = []

                    # Process code examples in parallel
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=10
                    ) as executor:
                        # Prepare arguments for parallel processing
                        summary_args = [
                            (
                                block["code"],
                                block["context_before"],
                                block["context_after"],
                            )
                            for block in code_blocks
                        ]

                        # Generate summaries in parallel
                        summaries = list(
                            executor.map(process_code_example, summary_args)
                        )

                    # Prepare code example data
                    for i, (block, summary) in enumerate(zip(code_blocks, summaries)):
                        code_urls.append(url)
                        code_chunk_numbers.append(i)
                        code_examples.append(block["code"])
                        code_summaries.append(summary)

                        # Create metadata for code example
                        code_meta = {
                            "chunk_index": i,
                            "url": url,
                            "source": source_id,
                            "char_count": len(block["code"]),
                            "word_count": len(block["code"].split()),
                        }
                        code_metadatas.append(code_meta)

                    # Add code examples to Supabase
                    add_code_examples_to_supabase(
                        supabase_client,
                        code_urls,
                        code_chunk_numbers,
                        code_examples,
                        code_summaries,
                        code_metadatas,
                    )

            return json.dumps(
                {
                    "success": True,
                    "url": url,
                    "chunks_stored": len(chunks),
                    "code_examples_stored": len(code_blocks) if code_blocks else 0,
                    "content_length": len(result.markdown),
                    "total_word_count": total_word_count,
                    "source_id": source_id,
                    "links_count": {
                        "internal": len(result.links.get("internal", [])),
                        "external": len(result.links.get("external", [])),
                    },
                },
                indent=2,
            )
        else:
            return json.dumps(
                {"success": False, "url": url, "error": result.error_message}, indent=2
            )
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


@mcp.tool()
async def crawl_with_stealth_mode(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
    wait_for_selector: str = "",
    extra_wait: int = 2
) -> str:
    """
    Crawl URLs using undetected browser mode to bypass bot protection (Cloudflare, Akamai, etc.).
    
    This tool uses stealth browser technology to appear as a regular user, making it ideal for:
    - Sites with Cloudflare protection
    - Sites with bot detection (Akamai, PerimeterX, etc.)
    - Sites that block headless browsers
    - Content behind aggressive anti-scraping measures
    
    Args:
        ctx: The MCP server provided context
        url: URL to crawl (can be a regular webpage, sitemap.xml, or .txt file)
        max_depth: Maximum recursion depth for regular URLs (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)
        chunk_size: Maximum size of each content chunk in characters (default: 5000)
        wait_for_selector: Optional CSS selector to wait for before extracting content
        extra_wait: Additional wait time in seconds after page load (default: 2)
    
    Returns:
        JSON string with crawl summary, storage information, and success statistics
    
    Example:
        # Bypass Cloudflare-protected site
        crawl_with_stealth_mode("https://example.com", wait_for_selector="div.content", extra_wait=3)
    """
    try:
        # Get supabase client from context
        supabase_client = ctx.request_context.lifespan_context.supabase_client
        
        # Determine crawl strategy
        crawl_results = []
        crawl_type = None
        
        # Configure undetected browser for stealth mode
        browser_config = BrowserConfig(
            browser_type="undetected",  # Use undetected-chromedriver
            headless=True,
            verbose=False,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )
        
        # Initialize crawler with stealth configuration
        async with AsyncWebCrawler(config=browser_config) as stealth_crawler:
            if is_txt(url):
                # For text files, use simple crawl
                crawl_results = await crawl_markdown_file(stealth_crawler, url)
                crawl_type = "text_file"
            elif is_sitemap(url):
                # For sitemaps, extract URLs and crawl in parallel
                sitemap_urls = parse_sitemap(url)
                if not sitemap_urls:
                    return json.dumps(
                        {"success": False, "url": url, "error": "No URLs found in sitemap"},
                        indent=2,
                    )
                crawl_results = await crawl_batch(
                    stealth_crawler, sitemap_urls, max_concurrent=max_concurrent
                )
                crawl_type = "sitemap"
            else:
                # For regular pages, crawl recursively
                crawl_results = await crawl_recursive_internal_links(
                    stealth_crawler, [url], max_depth=max_depth, max_concurrent=max_concurrent
                )
                crawl_type = "webpage"
            
            # Process and store results (same as smart_crawl_url)
            if not crawl_results:
                return json.dumps(
                    {"success": False, "url": url, "error": "No content found"},
                    indent=2,
                )
            
            # Process results and store in Supabase (identical to smart_crawl_url)
            urls = []
            chunk_numbers = []
            contents = []
            metadatas = []
            chunk_count = 0
            
            source_content_map = {}
            source_word_counts = {}
            
            for doc in crawl_results:
                source_url = doc["url"]
                md = doc["markdown"]
                chunks = smart_chunk_markdown(md, chunk_size=chunk_size)
                
                parsed_url = urlparse(source_url)
                source_id = parsed_url.netloc or parsed_url.path
                
                if source_id not in source_content_map:
                    source_content_map[source_id] = md[:5000]
                    source_word_counts[source_id] = 0
                
                for i, chunk in enumerate(chunks):
                    urls.append(source_url)
                    chunk_numbers.append(i)
                    contents.append(chunk)
                    
                    meta = extract_section_info(chunk)
                    meta["chunk_index"] = i
                    meta["url"] = source_url
                    meta["source"] = source_id
                    meta["crawl_type"] = "stealth_" + crawl_type
                    meta["stealth_mode"] = True
                    metadatas.append(meta)
                    
                    chunk_count += 1
                    source_word_counts[source_id] += len(chunk.split())
            
            # Update source information for each unique source FIRST (before inserting documents)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                source_summary_args = [
                    (source_id, content)
                    for source_id, content in source_content_map.items()
                ]
                source_summaries = list(
                    executor.map(
                        lambda args: extract_source_summary(args[0], args[1]),
                        source_summary_args,
                    )
                )

            for (source_id, _), summary in zip(source_summary_args, source_summaries):
                word_count = source_word_counts.get(source_id, 0)
                update_source_info(supabase_client, source_id, summary, word_count)

            # Store documents (AFTER sources exist)
            if contents:
                url_to_full_doc = {
                    doc["url"]: doc["markdown"] for doc in crawl_results
                }
                add_documents_to_supabase(
                    supabase_client,
                    urls,
                    chunk_numbers,
                    contents,
                    metadatas,
                    url_to_full_doc,
                )
            
            return json.dumps(
                {
                    "success": True,
                    "crawl_type": "stealth_" + crawl_type,
                    "url": url,
                    "mode": "stealth (undetected browser)",
                    "pages_crawled": len(crawl_results),
                    "total_chunks": chunk_count,
                },
                indent=2,
            )
    
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


@mcp.tool()
async def smart_crawl_url(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
) -> str:
    """
    Intelligently crawl a URL based on its type and store content in Supabase.

    This tool automatically detects the URL type and applies the appropriate crawling method:
    - For sitemaps: Extracts and crawls all URLs in parallel
    - For text files (llms.txt): Directly retrieves the content
    - For regular webpages: Recursively crawls internal links up to the specified depth

    All crawled content is chunked and stored in Supabase for later retrieval and querying.

    Args:
        ctx: The MCP server provided context
        url: URL to crawl (can be a regular webpage, sitemap.xml, or .txt file)
        max_depth: Maximum recursion depth for regular URLs (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)
        chunk_size: Maximum size of each content chunk in characters (default: 1000)

    Returns:
        JSON string with crawl summary and storage information
    """
    try:
        # Get the crawler from the context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Determine the crawl strategy
        crawl_results = []
        crawl_type = None

        if is_txt(url):
            # For text files, use simple crawl
            crawl_results = await crawl_markdown_file(crawler, url)
            crawl_type = "text_file"
        elif is_sitemap(url):
            # For sitemaps, extract URLs and crawl in parallel
            sitemap_urls = parse_sitemap(url)
            if not sitemap_urls:
                return json.dumps(
                    {"success": False, "url": url, "error": "No URLs found in sitemap"},
                    indent=2,
                )
            crawl_results = await crawl_batch(
                crawler, sitemap_urls, max_concurrent=max_concurrent
            )
            crawl_type = "sitemap"
        else:
            # For regular URLs, use recursive crawl
            crawl_results = await crawl_recursive_internal_links(
                crawler, [url], max_depth=max_depth, max_concurrent=max_concurrent
            )
            crawl_type = "webpage"

        if not crawl_results:
            return json.dumps(
                {"success": False, "url": url, "error": "No content found"}, indent=2
            )

        # Process results and store in Supabase
        urls = []
        chunk_numbers = []
        contents = []
        metadatas = []
        chunk_count = 0

        # Track sources and their content
        source_content_map = {}
        source_word_counts = {}

        # Process documentation chunks
        for doc in crawl_results:
            source_url = doc["url"]
            md = doc["markdown"]
            chunks = smart_chunk_markdown(md, chunk_size=chunk_size)

            # Extract source_id
            parsed_url = urlparse(source_url)
            source_id = parsed_url.netloc or parsed_url.path

            # Store content for source summary generation
            if source_id not in source_content_map:
                source_content_map[source_id] = md[:5000]  # Store first 5000 chars
                source_word_counts[source_id] = 0

            for i, chunk in enumerate(chunks):
                urls.append(source_url)
                chunk_numbers.append(i)
                contents.append(chunk)

                # Extract metadata
                meta = extract_section_info(chunk)
                meta["chunk_index"] = i
                meta["url"] = source_url
                meta["source"] = source_id
                meta["crawl_type"] = crawl_type
                meta["crawl_time"] = str(asyncio.current_task().get_coro().__name__)
                metadatas.append(meta)

                # Accumulate word count
                source_word_counts[source_id] += meta.get("word_count", 0)

                chunk_count += 1

        # Create url_to_full_document mapping
        url_to_full_document = {}
        for doc in crawl_results:
            url_to_full_document[doc["url"]] = doc["markdown"]

        # Update source information for each unique source FIRST (before inserting documents)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            source_summary_args = [
                (source_id, content)
                for source_id, content in source_content_map.items()
            ]
            source_summaries = list(
                executor.map(
                    lambda args: extract_source_summary(args[0], args[1]),
                    source_summary_args,
                )
            )

        for (source_id, _), summary in zip(source_summary_args, source_summaries):
            word_count = source_word_counts.get(source_id, 0)
            update_source_info(supabase_client, source_id, summary, word_count)

        # Add documentation chunks to Supabase (AFTER sources exist)
        batch_size = 20
        add_documents_to_supabase(
            supabase_client,
            urls,
            chunk_numbers,
            contents,
            metadatas,
            url_to_full_document,
            batch_size=batch_size,
        )

        # Extract and process code examples from all documents only if enabled
        extract_code_examples_enabled = os.getenv("USE_AGENTIC_RAG", "false") == "true"
        if extract_code_examples_enabled:
            all_code_blocks = []
            code_urls = []
            code_chunk_numbers = []
            code_examples = []
            code_summaries = []
            code_metadatas = []

            # Extract code blocks from all documents
            for doc in crawl_results:
                source_url = doc["url"]
                md = doc["markdown"]
                code_blocks = extract_code_blocks(md)

                if code_blocks:
                    # Process code examples in parallel
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=10
                    ) as executor:
                        # Prepare arguments for parallel processing
                        summary_args = [
                            (
                                block["code"],
                                block["context_before"],
                                block["context_after"],
                            )
                            for block in code_blocks
                        ]

                        # Generate summaries in parallel
                        summaries = list(
                            executor.map(process_code_example, summary_args)
                        )

                    # Prepare code example data
                    parsed_url = urlparse(source_url)
                    source_id = parsed_url.netloc or parsed_url.path

                    for i, (block, summary) in enumerate(zip(code_blocks, summaries)):
                        code_urls.append(source_url)
                        code_chunk_numbers.append(
                            len(code_examples)
                        )  # Use global code example index
                        code_examples.append(block["code"])
                        code_summaries.append(summary)

                        # Create metadata for code example
                        code_meta = {
                            "chunk_index": len(code_examples) - 1,
                            "url": source_url,
                            "source": source_id,
                            "char_count": len(block["code"]),
                            "word_count": len(block["code"].split()),
                        }
                        code_metadatas.append(code_meta)

            # Add all code examples to Supabase
            if code_examples:
                add_code_examples_to_supabase(
                    supabase_client,
                    code_urls,
                    code_chunk_numbers,
                    code_examples,
                    code_summaries,
                    code_metadatas,
                    batch_size=batch_size,
                )

        return json.dumps(
            {
                "success": True,
                "url": url,
                "crawl_type": crawl_type,
                "pages_crawled": len(crawl_results),
                "chunks_stored": chunk_count,
                "code_examples_stored": len(code_examples),
                "sources_updated": len(source_content_map),
                "urls_crawled": [doc["url"] for doc in crawl_results][:5]
                + (["..."] if len(crawl_results) > 5 else []),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


@mcp.tool()
async def crawl_with_multi_url_config(
    ctx: Context,
    urls_json: str,
    max_concurrent: int = 5,
    chunk_size: int = 5000
) -> str:
    """
    Crawl multiple URLs with smart per-URL configuration based on content type patterns.
    
    This tool automatically optimizes crawler settings for different types of content:
    - Documentation sites: Wait for code blocks, extra parsing time
    - News/articles: Focus on main content, minimal wait
    - E-commerce: Wait for dynamic pricing, product details
    - Forums/discussions: Handle infinite scroll, wait for comments
    
    Args:
        ctx: The MCP server provided context
        urls_json: JSON array of URLs to crawl with smart configuration
                   Example: '["https://docs.python.org", "https://news.example.com"]'
        max_concurrent: Maximum number of concurrent browser sessions (default: 5)
        chunk_size: Maximum size of each content chunk in characters (default: 5000)
    
    Returns:
        JSON string with crawl summary for each URL and aggregate statistics
    
    Example:
        # Crawl multiple site types with optimized settings
        urls = '["https://docs.example.com", "https://api.example.com"]'
        crawl_with_multi_url_config(urls)
    """
    try:
        # Get clients from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client
        
        # Parse URL list
        try:
            url_list = json.loads(urls_json)
            if not isinstance(url_list, list):
                return json.dumps({"error": "urls_json must be a JSON array of URLs"})
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON: {str(e)}"})
        
        results = []
        total_chunks = 0
        
        # Process each URL with optimized configuration
        for url in url_list:
            # Determine content type and create appropriate config
            if any(kw in url.lower() for kw in ["docs", "documentation", "api", "reference"]):
                # Documentation: wait for code rendering
                config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=50,
                    css_selector="article, main, .content, .documentation",
                )
                content_type = "documentation"
            
            elif any(kw in url.lower() for kw in ["news", "article", "blog", "post"]):
                # News/articles: focus on main content
                config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=100,
                    css_selector="article, main, .post-content, .article-body",
                )
                content_type = "article"
            
            else:
                # Default: general purpose
                config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                content_type = "general"
            
            # Crawl this URL
            crawl_results = await crawl_recursive_internal_links(
                crawler, [url], max_depth=2, max_concurrent=max_concurrent
            )
            
            if not crawl_results:
                results.append({
                    "url": url,
                    "content_type": content_type,
                    "success": False,
                    "error": "No content found"
                })
                continue
            
            # Process and store (same as smart_crawl_url)
            urls_list = []
            chunk_numbers = []
            contents = []
            metadatas = []
            
            for doc in crawl_results:
                source_url = doc["url"]
                md = doc["markdown"]
                chunks = smart_chunk_markdown(md, chunk_size=chunk_size)
                
                parsed_url = urlparse(source_url)
                source_id = parsed_url.netloc or parsed_url.path
                
                for i, chunk in enumerate(chunks):
                    urls_list.append(source_url)
                    chunk_numbers.append(i)
                    contents.append(chunk)
                    
                    meta = extract_section_info(chunk)
                    meta["chunk_index"] = i
                    meta["url"] = source_url
                    meta["source"] = source_id
                    meta["crawl_type"] = "multi_url"
                    meta["content_type"] = content_type
                    metadatas.append(meta)
            
            # Store documents
            if contents:
                url_to_full_doc = {
                    doc["url"]: doc["markdown"] for doc in crawl_results
                }

                # Create/update source in sources table FIRST (before inserting documents)
                # Extract source_id from the first URL (all URLs in this batch have same domain)
                parsed_url = urlparse(url)
                source_id = parsed_url.netloc or parsed_url.path

                # Generate source summary from first document
                first_doc_content = crawl_results[0]["markdown"][:5000] if crawl_results else ""
                source_summary = extract_source_summary(source_id, first_doc_content)

                # Calculate total word count for this source
                total_word_count = sum(len(doc["markdown"].split()) for doc in crawl_results)

                # Update source info (creates source if it doesn't exist)
                update_source_info(supabase_client, source_id, source_summary, total_word_count)

                # Now add documents to Supabase (AFTER source exists)
                add_documents_to_supabase(
                    supabase_client,
                    urls_list,
                    chunk_numbers,
                    contents,
                    metadatas,
                    url_to_full_doc,
                )
            
            results.append({
                "url": url,
                "content_type": content_type,
                "success": True,
                "pages_crawled": len(crawl_results),
                "chunks_stored": len(contents)
            })
            total_chunks += len(contents)
        
        return json.dumps(
            {
                "success": True,
                "urls_processed": len(url_list),
                "total_chunks": total_chunks,
                "results": results
            },
            indent=2,
        )
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
async def crawl_with_memory_monitoring(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
    memory_threshold_mb: int = 500
) -> str:
    """
    Crawl URLs with active memory monitoring and adaptive throttling.
    
    This tool monitors memory usage during large-scale crawling operations and automatically
    adjusts concurrency to prevent memory exhaustion. Ideal for:
    - Large-scale documentation sites (1000+ pages)
    - Sites with heavy media content
    - Long-running crawl operations
    - Resource-constrained environments
    
    Args:
        ctx: The MCP server provided context
        url: URL to crawl (sitemap, webpage, or text file)
        max_depth: Maximum recursion depth (default: 3)
        max_concurrent: Initial concurrent sessions (auto-adjusted, default: 10)
        chunk_size: Chunk size in characters (default: 5000)
        memory_threshold_mb: Memory limit in MB before throttling (default: 500)
    
    Returns:
        JSON string with crawl summary and memory statistics
    
    Example:
        # Crawl large site with memory monitoring
        crawl_with_memory_monitoring("https://docs.example.com/sitemap.xml", memory_threshold_mb=300)
    """
    try:
        import psutil
        import time
        
        # Get clients from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client
        
        # Memory monitoring setup
        process = psutil.Process()
        start_memory_mb = process.memory_info().rss / 1024 / 1024
        peak_memory_mb = start_memory_mb
        memory_samples = []
        start_time = time.time()
        
        # Determine crawl strategy
        crawl_results = []
        crawl_type = None
        
        if is_txt(url):
            crawl_results = await crawl_markdown_file(crawler, url)
            crawl_type = "text_file"
        elif is_sitemap(url):
            sitemap_urls = parse_sitemap(url)
            if not sitemap_urls:
                return json.dumps(
                    {"success": False, "url": url, "error": "No URLs found in sitemap"},
                    indent=2,
                )
            
            # Crawl in batches with memory monitoring
            batch_size = max_concurrent
            for i in range(0, len(sitemap_urls), batch_size):
                # Check memory before each batch
                current_memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory_mb)
                peak_memory_mb = max(peak_memory_mb, current_memory_mb)
                
                # Adaptive throttling
                if current_memory_mb > memory_threshold_mb:
                    batch_size = max(1, batch_size // 2)  # Reduce concurrency
                
                batch = sitemap_urls[i:i + batch_size]
                batch_results = await crawl_batch(crawler, batch, max_concurrent=batch_size)
                crawl_results.extend(batch_results)
            
            crawl_type = "sitemap"
        else:
            crawl_results = await crawl_recursive_internal_links(
                crawler, [url], max_depth=max_depth, max_concurrent=max_concurrent
            )
            crawl_type = "webpage"
        
        if not crawl_results:
            return json.dumps(
                {"success": False, "url": url, "error": "No content found"}, indent=2
            )
        
        # Process and store results (same as smart_crawl_url)
        urls_list = []
        chunk_numbers = []
        contents = []
        metadatas = []
        chunk_count = 0

        source_content_map = {}
        source_word_counts = {}

        for doc in crawl_results:
            source_url = doc["url"]
            md = doc["markdown"]
            chunks = smart_chunk_markdown(md, chunk_size=chunk_size)

            parsed_url = urlparse(source_url)
            source_id = parsed_url.netloc or parsed_url.path

            if source_id not in source_content_map:
                source_content_map[source_id] = md[:5000]
                source_word_counts[source_id] = 0

            for i, chunk in enumerate(chunks):
                urls_list.append(source_url)
                chunk_numbers.append(i)
                contents.append(chunk)

                meta = extract_section_info(chunk)
                meta["chunk_index"] = i
                meta["url"] = source_url
                meta["source"] = source_id
                meta["crawl_type"] = "memory_monitored_" + crawl_type
                metadatas.append(meta)

                chunk_count += 1
                source_word_counts[source_id] += len(chunk.split())

        # Update source information for each unique source FIRST (before inserting documents)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            source_summary_args = [
                (source_id, content)
                for source_id, content in source_content_map.items()
            ]
            source_summaries = list(
                executor.map(
                    lambda args: extract_source_summary(args[0], args[1]),
                    source_summary_args,
                )
            )

        for (source_id, _), summary in zip(source_summary_args, source_summaries):
            word_count = source_word_counts.get(source_id, 0)
            update_source_info(supabase_client, source_id, summary, word_count)

        # Store documents (AFTER sources exist)
        if contents:
            url_to_full_doc = {
                doc["url"]: doc["markdown"] for doc in crawl_results
            }
            add_documents_to_supabase(
                supabase_client,
                urls_list,
                chunk_numbers,
                contents,
                metadatas,
                url_to_full_doc,
            )
        
        # Final memory stats
        end_memory_mb = process.memory_info().rss / 1024 / 1024
        elapsed_time = time.time() - start_time
        
        return json.dumps(
            {
                "success": True,
                "crawl_type": "memory_monitored_" + crawl_type,
                "url": url,
                "pages_crawled": len(crawl_results),
                "total_chunks": chunk_count,
                "memory_stats": {
                    "start_mb": round(start_memory_mb, 2),
                    "end_mb": round(end_memory_mb, 2),
                    "peak_mb": round(peak_memory_mb, 2),
                    "delta_mb": round(end_memory_mb - start_memory_mb, 2),
                    "avg_mb": round(sum(memory_samples) / len(memory_samples), 2) if memory_samples else 0,
                    "threshold_mb": memory_threshold_mb,
                    "elapsed_seconds": round(elapsed_time, 2),
                },
            },
            indent=2,
        )
    
    except ImportError:
        return json.dumps({
            "success": False,
            "error": "psutil library required for memory monitoring. Install with: pip install psutil"
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


@mcp.tool()
async def get_available_sources(ctx: Context) -> str:
    """
    Get all available sources from the sources table.

    This tool returns a list of all unique sources (domains) that have been crawled and stored
    in the database, along with their summaries and statistics. This is useful for discovering
    what content is available for querying.

    Always use this tool before calling the RAG query or code example query tool
    with a specific source filter!

    Args:
        ctx: The MCP server provided context

    Returns:
        JSON string with the list of available sources and their details
    """
    try:
        # Get the Supabase client from the context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Query the sources table directly
        result = (
            supabase_client.from_("sources").select("*").order("source_id").execute()
        )

        # Format the sources with their details
        sources = []
        if result.data:
            for source in result.data:
                sources.append(
                    {
                        "source_id": source.get("source_id"),
                        "summary": source.get("summary"),
                        "total_words": source.get("total_words"),
                        "created_at": source.get("created_at"),
                        "updated_at": source.get("updated_at"),
                    }
                )

        return json.dumps(
            {"success": True, "sources": sources, "count": len(sources)}, indent=2
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
async def perform_rag_query(
    ctx: Context, query: str, source: str = None, match_count: int = 5
) -> str:
    """
    Perform a RAG (Retrieval Augmented Generation) query on the stored content.

    This tool searches the vector database for content relevant to the query and returns
    the matching documents. Optionally filter by source domain.
    Get the source by using the get_available_sources tool before calling this search!

    Args:
        ctx: The MCP server provided context
        query: The search query
        source: Optional source domain to filter results (e.g., 'example.com')
        match_count: Maximum number of results to return (default: 5)

    Returns:
        JSON string with the search results
    """
    try:
        # Get the Supabase client from the context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"

        # Prepare filter if source is provided and not empty
        filter_metadata = None
        if source and source.strip():
            filter_metadata = {"source": source}

        if use_hybrid_search:
            # Hybrid search: combine vector and keyword search

            # 1. Get vector search results (get more to account for filtering)
            vector_results = search_documents(
                client=supabase_client,
                query=query,
                match_count=match_count * 2,  # Get double to have room for filtering
                filter_metadata=filter_metadata,
            )

            # 2. Get keyword search results using ILIKE
            keyword_query = (
                supabase_client.from_("crawled_pages")
                .select("id, url, chunk_number, content, metadata, source_id")
                .ilike("content", f"%{query}%")
            )

            # Apply source filter if provided
            if source and source.strip():
                keyword_query = keyword_query.eq("source_id", source)

            # Execute keyword search
            keyword_response = keyword_query.limit(match_count * 2).execute()
            keyword_results = keyword_response.data if keyword_response.data else []

            # 3. Combine results with preference for items appearing in both
            seen_ids = set()
            combined_results = []

            # First, add items that appear in both searches (these are the best matches)
            vector_ids = {r.get("id") for r in vector_results if r.get("id")}
            for kr in keyword_results:
                if kr["id"] in vector_ids and kr["id"] not in seen_ids:
                    # Find the vector result to get similarity score
                    for vr in vector_results:
                        if vr.get("id") == kr["id"]:
                            # Boost similarity score for items in both results
                            vr["similarity"] = min(1.0, vr.get("similarity", 0) * 1.2)
                            combined_results.append(vr)
                            seen_ids.add(kr["id"])
                            break

            # Then add remaining vector results (semantic matches without exact keyword)
            for vr in vector_results:
                if (
                    vr.get("id")
                    and vr["id"] not in seen_ids
                    and len(combined_results) < match_count
                ):
                    combined_results.append(vr)
                    seen_ids.add(vr["id"])

            # Finally, add pure keyword matches if we still need more results
            for kr in keyword_results:
                if kr["id"] not in seen_ids and len(combined_results) < match_count:
                    # Convert keyword result to match vector result format
                    combined_results.append(
                        {
                            "id": kr["id"],
                            "url": kr["url"],
                            "chunk_number": kr["chunk_number"],
                            "content": kr["content"],
                            "metadata": kr["metadata"],
                            "source_id": kr["source_id"],
                            "similarity": 0.5,  # Default similarity for keyword-only matches
                        }
                    )
                    seen_ids.add(kr["id"])

            # Use combined results
            results = combined_results[:match_count]

        else:
            # Standard vector search only
            results = search_documents(
                client=supabase_client,
                query=query,
                match_count=match_count,
                filter_metadata=filter_metadata,
            )

        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(
                ctx.request_context.lifespan_context.reranking_model,
                query,
                results,
                content_key="content",
            )

        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result.get("url"),
                "content": result.get("content"),
                "metadata": result.get("metadata"),
                "similarity": result.get("similarity"),
            }
            # Include rerank score if available
            if "rerank_score" in result:
                formatted_result["rerank_score"] = result["rerank_score"]
            formatted_results.append(formatted_result)

        return json.dumps(
            {
                "success": True,
                "query": query,
                "source_filter": source,
                "search_mode": "hybrid" if use_hybrid_search else "vector",
                "reranking_applied": use_reranking
                and ctx.request_context.lifespan_context.reranking_model is not None,
                "results": formatted_results,
                "count": len(formatted_results),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "query": query, "error": str(e)}, indent=2)


@mcp.tool()
async def search_code_examples(
    ctx: Context, query: str, source_id: str = None, match_count: int = 5
) -> str:
    """
    Search for code examples relevant to the query.

    This tool searches the vector database for code examples relevant to the query and returns
    the matching examples with their summaries. Optionally filter by source_id.
    Get the source_id by using the get_available_sources tool before calling this search!

    Use the get_available_sources tool first to see what sources are available for filtering.

    Args:
        ctx: The MCP server provided context
        query: The search query
        source_id: Optional source ID to filter results (e.g., 'example.com')
        match_count: Maximum number of results to return (default: 5)

    Returns:
        JSON string with the search results
    """
    # Check if code example extraction is enabled
    extract_code_examples_enabled = os.getenv("USE_AGENTIC_RAG", "false") == "true"
    if not extract_code_examples_enabled:
        return json.dumps(
            {
                "success": False,
                "error": "Code example extraction is disabled. Perform a normal RAG search.",
            },
            indent=2,
        )

    try:
        # Get the Supabase client from the context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"

        # Prepare filter if source is provided and not empty
        filter_metadata = None
        if source_id and source_id.strip():
            filter_metadata = {"source": source_id}

        if use_hybrid_search:
            # Hybrid search: combine vector and keyword search

            # Import the search function from utils
            from utils import search_code_examples as search_code_examples_impl

            # 1. Get vector search results (get more to account for filtering)
            vector_results = search_code_examples_impl(
                client=supabase_client,
                query=query,
                match_count=match_count * 2,  # Get double to have room for filtering
                filter_metadata=filter_metadata,
            )

            # 2. Get keyword search results using ILIKE on both content and summary
            keyword_query = (
                supabase_client.from_("code_examples")
                .select("id, url, chunk_number, content, summary, metadata, source_id")
                .or_(f"content.ilike.%{query}%,summary.ilike.%{query}%")
            )

            # Apply source filter if provided
            if source_id and source_id.strip():
                keyword_query = keyword_query.eq("source_id", source_id)

            # Execute keyword search
            keyword_response = keyword_query.limit(match_count * 2).execute()
            keyword_results = keyword_response.data if keyword_response.data else []

            # 3. Combine results with preference for items appearing in both
            seen_ids = set()
            combined_results = []

            # First, add items that appear in both searches (these are the best matches)
            vector_ids = {r.get("id") for r in vector_results if r.get("id")}
            for kr in keyword_results:
                if kr["id"] in vector_ids and kr["id"] not in seen_ids:
                    # Find the vector result to get similarity score
                    for vr in vector_results:
                        if vr.get("id") == kr["id"]:
                            # Boost similarity score for items in both results
                            vr["similarity"] = min(1.0, vr.get("similarity", 0) * 1.2)
                            combined_results.append(vr)
                            seen_ids.add(kr["id"])
                            break

            # Then add remaining vector results (semantic matches without exact keyword)
            for vr in vector_results:
                if (
                    vr.get("id")
                    and vr["id"] not in seen_ids
                    and len(combined_results) < match_count
                ):
                    combined_results.append(vr)
                    seen_ids.add(vr["id"])

            # Finally, add pure keyword matches if we still need more results
            for kr in keyword_results:
                if kr["id"] not in seen_ids and len(combined_results) < match_count:
                    # Convert keyword result to match vector result format
                    combined_results.append(
                        {
                            "id": kr["id"],
                            "url": kr["url"],
                            "chunk_number": kr["chunk_number"],
                            "content": kr["content"],
                            "summary": kr["summary"],
                            "metadata": kr["metadata"],
                            "source_id": kr["source_id"],
                            "similarity": 0.5,  # Default similarity for keyword-only matches
                        }
                    )
                    seen_ids.add(kr["id"])

            # Use combined results
            results = combined_results[:match_count]

        else:
            # Standard vector search only
            from utils import search_code_examples as search_code_examples_impl

            results = search_code_examples_impl(
                client=supabase_client,
                query=query,
                match_count=match_count,
                filter_metadata=filter_metadata,
            )

        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(
                ctx.request_context.lifespan_context.reranking_model,
                query,
                results,
                content_key="content",
            )

        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result.get("url"),
                "code": result.get("content"),
                "summary": result.get("summary"),
                "metadata": result.get("metadata"),
                "source_id": result.get("source_id"),
                "similarity": result.get("similarity"),
            }
            # Include rerank score if available
            if "rerank_score" in result:
                formatted_result["rerank_score"] = result["rerank_score"]
            formatted_results.append(formatted_result)

        return json.dumps(
            {
                "success": True,
                "query": query,
                "source_filter": source_id,
                "search_mode": "hybrid" if use_hybrid_search else "vector",
                "reranking_applied": use_reranking
                and ctx.request_context.lifespan_context.reranking_model is not None,
                "results": formatted_results,
                "count": len(formatted_results),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "query": query, "error": str(e)}, indent=2)


@mcp.tool()
async def check_ai_script_hallucinations(ctx: Context, script_path: str) -> str:
    """
    Check an AI-generated Python script for hallucinations using the knowledge graph.

    This tool analyzes a Python script for potential AI hallucinations by validating
    imports, method calls, class instantiations, and function calls against a Neo4j
    knowledge graph containing real repository data.

    The tool performs comprehensive analysis including:
    - Import validation against known repositories
    - Method call validation on classes from the knowledge graph
    - Class instantiation parameter validation
    - Function call parameter validation
    - Attribute access validation

    Args:
        ctx: The MCP server provided context
        script_path: Absolute path to the Python script to analyze

    Returns:
        JSON string with hallucination detection results, confidence scores, and recommendations
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the knowledge validator from context
        knowledge_validator = ctx.request_context.lifespan_context.knowledge_validator

        if not knowledge_validator:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph validator not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Validate script path
        validation = validate_script_path(script_path)
        if not validation["valid"]:
            return json.dumps(
                {
                    "success": False,
                    "script_path": script_path,
                    "error": validation["error"],
                },
                indent=2,
            )

        # Step 1: Analyze script structure using AST
        analyzer = AIScriptAnalyzer()
        analysis_result = analyzer.analyze_script(script_path)

        if analysis_result.errors:
            print(f"Analysis warnings for {script_path}: {analysis_result.errors}")

        # Step 2: Validate against knowledge graph
        validation_result = await knowledge_validator.validate_script(analysis_result)

        # Step 3: Generate comprehensive report
        reporter = HallucinationReporter()
        report = reporter.generate_comprehensive_report(validation_result)

        # Format response with comprehensive information
        return json.dumps(
            {
                "success": True,
                "script_path": script_path,
                "overall_confidence": validation_result.overall_confidence,
                "validation_summary": {
                    "total_validations": report["validation_summary"][
                        "total_validations"
                    ],
                    "valid_count": report["validation_summary"]["valid_count"],
                    "invalid_count": report["validation_summary"]["invalid_count"],
                    "uncertain_count": report["validation_summary"]["uncertain_count"],
                    "not_found_count": report["validation_summary"]["not_found_count"],
                    "hallucination_rate": report["validation_summary"][
                        "hallucination_rate"
                    ],
                },
                "hallucinations_detected": report["hallucinations_detected"],
                "recommendations": report["recommendations"],
                "analysis_metadata": {
                    "total_imports": report["analysis_metadata"]["total_imports"],
                    "total_classes": report["analysis_metadata"]["total_classes"],
                    "total_methods": report["analysis_metadata"]["total_methods"],
                    "total_attributes": report["analysis_metadata"]["total_attributes"],
                    "total_functions": report["analysis_metadata"]["total_functions"],
                },
                "libraries_analyzed": report.get("libraries_analyzed", []),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "script_path": script_path,
                "error": f"Analysis failed: {str(e)}",
            },
            indent=2,
        )


@mcp.tool()
async def query_knowledge_graph(ctx: Context, command: str) -> str:
    """
    Query and explore the Neo4j knowledge graph containing repository data.

    This tool provides comprehensive access to the knowledge graph for exploring repositories,
    classes, methods, functions, and their relationships. Perfect for understanding what data
    is available for hallucination detection and debugging validation results.

    **⚠️ IMPORTANT: Always start with the `repos` command first!**
    Before using any other commands, run `repos` to see what repositories are available
    in your knowledge graph. This will help you understand what data you can explore.

    ## Available Commands:

    **Repository Commands:**
    - `repos` - **START HERE!** List all repositories in the knowledge graph
    - `explore <repo_name>` - Get detailed overview of a specific repository

    **Class Commands:**
    - `classes` - List all classes across all repositories (limited to 20)
    - `classes <repo_name>` - List classes in a specific repository
    - `class <class_name>` - Get detailed information about a specific class including methods and attributes

    **Method Commands:**
    - `method <method_name>` - Search for methods by name across all classes
    - `method <method_name> <class_name>` - Search for a method within a specific class

    **Custom Query:**
    - `query <cypher_query>` - Execute a custom Cypher query (results limited to 20 records)

    ## Knowledge Graph Schema:

    **Node Types:**
    - Repository: `(r:Repository {name: string})`
    - File: `(f:File {path: string, module_name: string})`
    - Class: `(c:Class {name: string, full_name: string})`
    - Method: `(m:Method {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Function: `(func:Function {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Attribute: `(a:Attribute {name: string, type: string})`

    **Relationships:**
    - `(r:Repository)-[:CONTAINS]->(f:File)`
    - `(f:File)-[:DEFINES]->(c:Class)`
    - `(c:Class)-[:HAS_METHOD]->(m:Method)`
    - `(c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)`
    - `(f:File)-[:DEFINES]->(func:Function)`

    ## Example Workflow:
    ```
    1. repos                                    # See what repositories are available
    2. explore pydantic-ai                      # Explore a specific repository
    3. classes pydantic-ai                      # List classes in that repository
    4. class Agent                              # Explore the Agent class
    5. method run_stream                        # Search for run_stream method
    6. method __init__ Agent                    # Find Agent constructor
    7. query "MATCH (c:Class)-[:HAS_METHOD]->(m:Method) WHERE m.name = 'run' RETURN c.name, m.name LIMIT 5"
    ```

    Args:
        ctx: The MCP server provided context
        command: Command string to execute (see available commands above)

    Returns:
        JSON string with query results, statistics, and metadata
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get Neo4j driver from context
        repo_extractor = ctx.request_context.lifespan_context.repo_extractor
        if not repo_extractor or not repo_extractor.driver:
            return json.dumps(
                {
                    "success": False,
                    "error": "Neo4j connection not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Parse command
        command = command.strip()
        if not command:
            return json.dumps(
                {
                    "success": False,
                    "command": "",
                    "error": "Command cannot be empty. Available commands: repos, explore <repo>, classes [repo], class <name>, method <name> [class], query <cypher>",
                },
                indent=2,
            )

        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        async with repo_extractor.driver.session() as session:
            # Route to appropriate handler
            if cmd == "repos":
                return await _handle_repos_command(session, command)
            elif cmd == "explore":
                if not args:
                    return json.dumps(
                        {
                            "success": False,
                            "command": command,
                            "error": "Repository name required. Usage: explore <repo_name>",
                        },
                        indent=2,
                    )
                return await _handle_explore_command(session, command, args[0])
            elif cmd == "classes":
                repo_name = args[0] if args else None
                return await _handle_classes_command(session, command, repo_name)
            elif cmd == "class":
                if not args:
                    return json.dumps(
                        {
                            "success": False,
                            "command": command,
                            "error": "Class name required. Usage: class <class_name>",
                        },
                        indent=2,
                    )
                return await _handle_class_command(session, command, args[0])
            elif cmd == "method":
                if not args:
                    return json.dumps(
                        {
                            "success": False,
                            "command": command,
                            "error": "Method name required. Usage: method <method_name> [class_name]",
                        },
                        indent=2,
                    )
                method_name = args[0]
                class_name = args[1] if len(args) > 1 else None
                return await _handle_method_command(
                    session, command, method_name, class_name
                )
            elif cmd == "query":
                if not args:
                    return json.dumps(
                        {
                            "success": False,
                            "command": command,
                            "error": "Cypher query required. Usage: query <cypher_query>",
                        },
                        indent=2,
                    )
                cypher_query = " ".join(args)
                return await _handle_query_command(session, command, cypher_query)
            else:
                return json.dumps(
                    {
                        "success": False,
                        "command": command,
                        "error": f"Unknown command '{cmd}'. Available commands: repos, explore <repo>, classes [repo], class <name>, method <name> [class], query <cypher>",
                    },
                    indent=2,
                )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Query execution failed: {str(e)}",
            },
            indent=2,
        )


async def _handle_repos_command(session, command: str) -> str:
    """Handle 'repos' command - list all repositories"""
    query = "MATCH (r:Repository) RETURN r.name as name ORDER BY r.name"
    result = await session.run(query)

    repos = []
    async for record in result:
        repos.append(record["name"])

    return json.dumps(
        {
            "success": True,
            "command": command,
            "data": {"repositories": repos},
            "metadata": {"total_results": len(repos), "limited": False},
        },
        indent=2,
    )


async def _handle_explore_command(session, command: str, repo_name: str) -> str:
    """Handle 'explore <repo>' command - get repository overview"""
    # Check if repository exists
    repo_check_query = "MATCH (r:Repository {name: $repo_name}) RETURN r.name as name"
    result = await session.run(repo_check_query, repo_name=repo_name)
    repo_record = await result.single()

    if not repo_record:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Repository '{repo_name}' not found in knowledge graph",
            },
            indent=2,
        )

    # Get file count
    files_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)
    RETURN count(f) as file_count
    """
    result = await session.run(files_query, repo_name=repo_name)
    file_count = (await result.single())["file_count"]

    # Get class count
    classes_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
    RETURN count(DISTINCT c) as class_count
    """
    result = await session.run(classes_query, repo_name=repo_name)
    class_count = (await result.single())["class_count"]

    # Get function count
    functions_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(func:Function)
    RETURN count(DISTINCT func) as function_count
    """
    result = await session.run(functions_query, repo_name=repo_name)
    function_count = (await result.single())["function_count"]

    # Get method count
    methods_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_METHOD]->(m:Method)
    RETURN count(DISTINCT m) as method_count
    """
    result = await session.run(methods_query, repo_name=repo_name)
    method_count = (await result.single())["method_count"]

    return json.dumps(
        {
            "success": True,
            "command": command,
            "data": {
                "repository": repo_name,
                "statistics": {
                    "files": file_count,
                    "classes": class_count,
                    "functions": function_count,
                    "methods": method_count,
                },
            },
            "metadata": {"total_results": 1, "limited": False},
        },
        indent=2,
    )


async def _handle_classes_command(session, command: str, repo_name: str = None) -> str:
    """Handle 'classes [repo]' command - list classes"""
    limit = 20

    if repo_name:
        query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
        RETURN c.name as name, c.full_name as full_name
        ORDER BY c.name
        LIMIT $limit
        """
        result = await session.run(query, repo_name=repo_name, limit=limit)
    else:
        query = """
        MATCH (c:Class)
        RETURN c.name as name, c.full_name as full_name
        ORDER BY c.name
        LIMIT $limit
        """
        result = await session.run(query, limit=limit)

    classes = []
    async for record in result:
        classes.append({"name": record["name"], "full_name": record["full_name"]})

    return json.dumps(
        {
            "success": True,
            "command": command,
            "data": {"classes": classes, "repository_filter": repo_name},
            "metadata": {
                "total_results": len(classes),
                "limited": len(classes) >= limit,
            },
        },
        indent=2,
    )


async def _handle_class_command(session, command: str, class_name: str) -> str:
    """Handle 'class <name>' command - explore specific class"""
    # Find the class
    class_query = """
    MATCH (c:Class)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN c.name as name, c.full_name as full_name
    LIMIT 1
    """
    result = await session.run(class_query, class_name=class_name)
    class_record = await result.single()

    if not class_record:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Class '{class_name}' not found in knowledge graph",
            },
            indent=2,
        )

    actual_name = class_record["name"]
    full_name = class_record["full_name"]

    # Get methods
    methods_query = """
    MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN m.name as name, m.params_list as params_list, m.params_detailed as params_detailed, m.return_type as return_type
    ORDER BY m.name
    """
    result = await session.run(methods_query, class_name=class_name)

    methods = []
    async for record in result:
        # Use detailed params if available, fall back to simple params
        params_to_use = record["params_detailed"] or record["params_list"] or []
        methods.append(
            {
                "name": record["name"],
                "parameters": params_to_use,
                "return_type": record["return_type"] or "Any",
            }
        )

    # Get attributes
    attributes_query = """
    MATCH (c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN a.name as name, a.type as type
    ORDER BY a.name
    """
    result = await session.run(attributes_query, class_name=class_name)

    attributes = []
    async for record in result:
        attributes.append({"name": record["name"], "type": record["type"] or "Any"})

    return json.dumps(
        {
            "success": True,
            "command": command,
            "data": {
                "class": {
                    "name": actual_name,
                    "full_name": full_name,
                    "methods": methods,
                    "attributes": attributes,
                }
            },
            "metadata": {
                "total_results": 1,
                "methods_count": len(methods),
                "attributes_count": len(attributes),
                "limited": False,
            },
        },
        indent=2,
    )


async def _handle_method_command(
    session, command: str, method_name: str, class_name: str = None
) -> str:
    """Handle 'method <name> [class]' command - search for methods"""
    if class_name:
        query = """
        MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
        WHERE (c.name = $class_name OR c.full_name = $class_name)
          AND m.name = $method_name
        RETURN c.name as class_name, c.full_name as class_full_name,
               m.name as method_name, m.params_list as params_list,
               m.params_detailed as params_detailed, m.return_type as return_type, m.args as args
        """
        result = await session.run(
            query, class_name=class_name, method_name=method_name
        )
    else:
        query = """
        MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
        WHERE m.name = $method_name
        RETURN c.name as class_name, c.full_name as class_full_name,
               m.name as method_name, m.params_list as params_list,
               m.params_detailed as params_detailed, m.return_type as return_type, m.args as args
        ORDER BY c.name
        LIMIT 20
        """
        result = await session.run(query, method_name=method_name)

    methods = []
    async for record in result:
        # Use detailed params if available, fall back to simple params
        params_to_use = record["params_detailed"] or record["params_list"] or []
        methods.append(
            {
                "class_name": record["class_name"],
                "class_full_name": record["class_full_name"],
                "method_name": record["method_name"],
                "parameters": params_to_use,
                "return_type": record["return_type"] or "Any",
                "legacy_args": record["args"] or [],
            }
        )

    if not methods:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Method '{method_name}'"
                + (f" in class '{class_name}'" if class_name else "")
                + " not found",
            },
            indent=2,
        )

    return json.dumps(
        {
            "success": True,
            "command": command,
            "data": {"methods": methods, "class_filter": class_name},
            "metadata": {
                "total_results": len(methods),
                "limited": len(methods) >= 20 and not class_name,
            },
        },
        indent=2,
    )


async def _handle_query_command(session, command: str, cypher_query: str) -> str:
    """Handle 'query <cypher>' command - execute custom Cypher query"""
    try:
        # Execute the query with a limit to prevent overwhelming responses
        result = await session.run(cypher_query)

        records = []
        count = 0
        async for record in result:
            records.append(dict(record))
            count += 1
            if count >= 20:  # Limit results to prevent overwhelming responses
                break

        return json.dumps(
            {
                "success": True,
                "command": command,
                "data": {"query": cypher_query, "results": records},
                "metadata": {
                    "total_results": len(records),
                    "limited": len(records) >= 20,
                },
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Cypher query error: {str(e)}",
                "data": {"query": cypher_query},
            },
            indent=2,
        )


@mcp.tool()
async def parse_github_repository(ctx: Context, repo_url: str) -> str:
    """
    Parse a GitHub repository into the Neo4j knowledge graph.

    This tool clones a GitHub repository, analyzes its Python files, and stores
    the code structure (classes, methods, functions, imports) in Neo4j for use
    in hallucination detection. The tool:

    - Clones the repository to a temporary location
    - Analyzes Python files to extract code structure
    - Stores classes, methods, functions, and imports in Neo4j
    - Provides detailed statistics about the parsing results
    - Automatically handles module name detection for imports

    Args:
        ctx: The MCP server provided context
        repo_url: GitHub repository URL (e.g., 'https://github.com/user/repo.git')

    Returns:
        JSON string with parsing results, statistics, and repository information
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the repository extractor from context
        repo_extractor = ctx.request_context.lifespan_context.repo_extractor

        if not repo_extractor:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository extractor not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Validate repository URL
        validation = validate_github_url(repo_url)
        if not validation["valid"]:
            return json.dumps(
                {"success": False, "repo_url": repo_url, "error": validation["error"]},
                indent=2,
            )

        repo_name = validation["repo_name"]

        # Parse the repository (this includes cloning, analysis, and Neo4j storage)
        print(f"Starting repository analysis for: {repo_name}")
        await repo_extractor.analyze_repository(repo_url)
        print(f"Repository analysis completed for: {repo_name}")

        # Query Neo4j for statistics about the parsed repository
        async with repo_extractor.driver.session() as session:
            # Get comprehensive repository statistics
            stats_query = """
            MATCH (r:Repository {name: $repo_name})
            OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
            OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
            OPTIONAL MATCH (c)-[:HAS_ATTRIBUTE]->(a:Attribute)
            WITH r,
                 count(DISTINCT f) as files_count,
                 count(DISTINCT c) as classes_count,
                 count(DISTINCT m) as methods_count,
                 count(DISTINCT func) as functions_count,
                 count(DISTINCT a) as attributes_count

            // Get some sample module names
            OPTIONAL MATCH (r)-[:CONTAINS]->(sample_f:File)
            WITH r, files_count, classes_count, methods_count, functions_count, attributes_count,
                 collect(DISTINCT sample_f.module_name)[0..5] as sample_modules

            RETURN
                r.name as repo_name,
                files_count,
                classes_count,
                methods_count,
                functions_count,
                attributes_count,
                sample_modules
            """

            result = await session.run(stats_query, repo_name=repo_name)
            record = await result.single()

            if record:
                stats = {
                    "repository": record["repo_name"],
                    "files_processed": record["files_count"],
                    "classes_created": record["classes_count"],
                    "methods_created": record["methods_count"],
                    "functions_created": record["functions_count"],
                    "attributes_created": record["attributes_count"],
                    "sample_modules": record["sample_modules"] or [],
                }
            else:
                return json.dumps(
                    {
                        "success": False,
                        "repo_url": repo_url,
                        "error": f"Repository '{repo_name}' not found in database after parsing",
                    },
                    indent=2,
                )

        return json.dumps(
            {
                "success": True,
                "repo_url": repo_url,
                "repo_name": repo_name,
                "message": f"Successfully parsed repository '{repo_name}' into knowledge graph",
                "statistics": stats,
                "ready_for_validation": True,
                "next_steps": [
                    "Repository is now available for hallucination detection",
                    f"Use check_ai_script_hallucinations to validate scripts against {repo_name}",
                    "The knowledge graph contains classes, methods, and functions from this repository",
                ],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "repo_url": repo_url,
                "error": f"Repository parsing failed: {str(e)}",
            },
            indent=2,
        )


@mcp.tool()
async def parse_github_repositories_batch(
    ctx: Context,
    repo_urls_json: str,
    max_concurrent: int = 3,
    max_retries: int = 2
) -> str:
    """
    Parse multiple GitHub repositories into Neo4j knowledge graph in parallel.

    This tool efficiently processes multiple repositories with intelligent features:
    - Parallel processing with configurable concurrency limits
    - Automatic retry logic for transient failures
    - Detailed per-repository status tracking
    - Aggregate statistics and error reporting
    - Progress visibility for long-running operations

    Perfect for:
    - Bulk importing organization repositories
    - Building comprehensive knowledge graphs
    - Recovering from partial failures
    - Large-scale code analysis projects

    Args:
        ctx: The MCP server provided context
        repo_urls_json: JSON array of GitHub repository URLs
                       Example: '["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]'
        max_concurrent: Maximum number of repositories to process simultaneously (default: 3)
                       Lower values = less memory usage, higher values = faster completion
        max_retries: Number of retry attempts for failed repositories (default: 2)
                    Set to 0 to disable retries

    Returns:
        JSON string with:
        - Overall success status
        - Per-repository results with detailed status
        - Aggregate statistics (total, successful, failed)
        - Failed repositories list for easy retry
        - Processing time metrics

    Example:
        repos = '["https://github.com/openai/openai-python.git", "https://github.com/anthropics/anthropic-sdk-python.git"]'
        parse_github_repositories_batch(repos, max_concurrent=2, max_retries=1)
    """
    import asyncio
    import time
    from typing import Dict, Any, List

    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the repository extractor from context
        repo_extractor = ctx.request_context.lifespan_context.repo_extractor

        if not repo_extractor:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository extractor not available. Check Neo4j configuration.",
                },
                indent=2,
            )

        # Parse URL list
        try:
            repo_urls = json.loads(repo_urls_json)
            if not isinstance(repo_urls, list):
                return json.dumps({
                    "success": False,
                    "error": "repo_urls_json must be a JSON array of URLs"
                }, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"Invalid JSON: {str(e)}"
            }, indent=2)

        if not repo_urls:
            return json.dumps({
                "success": False,
                "error": "No repository URLs provided"
            }, indent=2)

        start_time = time.time()

        # Validate all URLs first
        validated_repos = []
        validation_errors = []

        for url in repo_urls:
            validation = validate_github_url(url)
            if validation["valid"]:
                validated_repos.append({
                    "url": url,
                    "name": validation["repo_name"]
                })
            else:
                validation_errors.append({
                    "url": url,
                    "error": validation["error"]
                })

        if not validated_repos:
            return json.dumps({
                "success": False,
                "error": "No valid repository URLs found",
                "validation_errors": validation_errors
            }, indent=2)

        # Track results for each repository
        results: List[Dict[str, Any]] = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_repo(repo_info: Dict[str, str], attempt: int = 1) -> Dict[str, Any]:
            """Process a single repository with retry logic."""
            async with semaphore:
                repo_url = repo_info["url"]
                repo_name = repo_info["name"]

                print(f"[{attempt}/{max_retries + 1}] Processing: {repo_name}")

                try:
                    # Parse the repository
                    await repo_extractor.analyze_repository(repo_url)

                    # Query Neo4j for statistics
                    async with repo_extractor.driver.session() as session:
                        stats_query = """
                        MATCH (r:Repository {name: $repo_name})
                        OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
                        OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
                        OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
                        OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
                        WITH r,
                             count(DISTINCT f) as files_count,
                             count(DISTINCT c) as classes_count,
                             count(DISTINCT m) as methods_count,
                             count(DISTINCT func) as functions_count
                        RETURN
                            r.name as repo_name,
                            files_count,
                            classes_count,
                            methods_count,
                            functions_count
                        """

                        result = await session.run(stats_query, repo_name=repo_name)
                        record = await result.single()

                        if record:
                            return {
                                "url": repo_url,
                                "repository": repo_name,
                                "status": "success",
                                "attempt": attempt,
                                "statistics": {
                                    "files_processed": record["files_count"],
                                    "classes_created": record["classes_count"],
                                    "methods_created": record["methods_count"],
                                    "functions_created": record["functions_count"],
                                }
                            }
                        else:
                            return {
                                "url": repo_url,
                                "repository": repo_name,
                                "status": "failed",
                                "attempt": attempt,
                                "error": "Repository processed but no data found in Neo4j"
                            }

                except Exception as e:
                    error_msg = str(e)
                    print(f"Error processing {repo_name} (attempt {attempt}): {error_msg}")

                    # Retry logic
                    if attempt <= max_retries:
                        print(f"Retrying {repo_name} in 2 seconds...")
                        await asyncio.sleep(2)  # Brief delay before retry
                        return await process_single_repo(repo_info, attempt + 1)
                    else:
                        return {
                            "url": repo_url,
                            "repository": repo_name,
                            "status": "failed",
                            "attempt": attempt,
                            "error": error_msg,
                            "retries_exhausted": True
                        }

        # Process all repositories in parallel (with concurrency limit)
        print(f"\nStarting batch processing of {len(validated_repos)} repositories...")
        print(f"Concurrency limit: {max_concurrent}, Max retries per repo: {max_retries}\n")

        tasks = [process_single_repo(repo) for repo in validated_repos]
        results = await asyncio.gather(*tasks)

        # Calculate aggregate statistics
        total_repos = len(results)
        successful_repos = [r for r in results if r["status"] == "success"]
        failed_repos = [r for r in results if r["status"] == "failed"]
        retried_repos = [r for r in results if r.get("attempt", 1) > 1]

        elapsed_time = time.time() - start_time

        # Build response
        response = {
            "success": len(failed_repos) == 0,
            "summary": {
                "total_repositories": total_repos,
                "successful": len(successful_repos),
                "failed": len(failed_repos),
                "retried": len(retried_repos),
                "validation_errors": len(validation_errors),
                "elapsed_seconds": round(elapsed_time, 2),
                "average_time_per_repo": round(elapsed_time / total_repos, 2) if total_repos > 0 else 0
            },
            "results": results,
        }

        # Add validation errors if any
        if validation_errors:
            response["validation_errors"] = validation_errors

        # Add failed repositories list for easy retry
        if failed_repos:
            response["failed_repositories"] = [
                {
                    "url": r["url"],
                    "repository": r["repository"],
                    "error": r.get("error", "Unknown error"),
                    "attempts": r.get("attempt", 1)
                }
                for r in failed_repos
            ]
            response["retry_urls"] = [r["url"] for r in failed_repos]

        # Add aggregate statistics for successful repos
        if successful_repos:
            total_files = sum(r["statistics"]["files_processed"] for r in successful_repos)
            total_classes = sum(r["statistics"]["classes_created"] for r in successful_repos)
            total_methods = sum(r["statistics"]["methods_created"] for r in successful_repos)
            total_functions = sum(r["statistics"]["functions_created"] for r in successful_repos)

            response["aggregate_statistics"] = {
                "total_files_processed": total_files,
                "total_classes_created": total_classes,
                "total_methods_created": total_methods,
                "total_functions_created": total_functions,
            }

        print(f"\nBatch processing complete!")
        print(f"✓ Successful: {len(successful_repos)}/{total_repos}")
        print(f"✗ Failed: {len(failed_repos)}/{total_repos}")
        if retried_repos:
            print(f"↻ Retried: {len(retried_repos)}")

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Batch processing failed: {str(e)}"
        }, indent=2)


async def crawl_markdown_file(
    crawler: AsyncWebCrawler, url: str
) -> List[Dict[str, Any]]:
    """
    Crawl a .txt or markdown file.

    Args:
        crawler: AsyncWebCrawler instance
        url: URL of the file

    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig()

    result = await crawler.arun(url=url, config=crawl_config)
    if result.success and result.markdown:
        return [{"url": url, "markdown": result.markdown}]
    else:
        print(f"Failed to crawl {url}: {result.error_message}")
        return []


async def crawl_batch(
    crawler: AsyncWebCrawler, urls: List[str], max_concurrent: int = 10
) -> List[Dict[str, Any]]:
    """
    Batch crawl multiple URLs in parallel.

    Args:
        crawler: AsyncWebCrawler instance
        urls: List of URLs to crawl
        max_concurrent: Maximum number of concurrent browser sessions

    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    results = await crawler.arun_many(
        urls=urls, config=crawl_config, dispatcher=dispatcher
    )
    return [
        {"url": r.url, "markdown": r.markdown}
        for r in results
        if r.success and r.markdown
    ]


# ============================================================================
# GraphRAG Tools - Document Knowledge Graph for Web Content
# ============================================================================


@mcp.tool()
async def crawl_with_graph_extraction(
    ctx: Context,
    url: str,
    extract_entities: bool = True,
    extract_relationships: bool = True,
    chunk_size: int = 5000
) -> str:
    """
    Crawl a URL and extract both vector embeddings (Supabase) and knowledge graph (Neo4j).

    This is the core GraphRAG crawl tool - it performs standard web crawling with
    vector embeddings PLUS extracts entities and relationships into a knowledge graph.

    Use this when you want rich, graph-augmented RAG capabilities where the system
    can understand entity relationships, dependencies, and connections.

    Args:
        ctx: The MCP server provided context
        url: URL to crawl
        extract_entities: Whether to extract entities (default: True)
        extract_relationships: Whether to extract relationships between entities (default: True)
        chunk_size: Size of text chunks for processing (default: 5000)

    Returns:
        JSON string with:
        - Crawl results (documents stored, chunks created)
        - Entity extraction results (entities found, relationships mapped)
        - Graph storage status
        - Statistics

    Example:
        crawl_with_graph_extraction("https://fastapi.tiangolo.com/")
    """
    try:
        # Check if GraphRAG is enabled
        graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
        if not graphrag_enabled:
            return json.dumps({
                "success": False,
                "error": "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment."
            }, indent=2)

        # Get components from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client
        document_graph_validator = ctx.request_context.lifespan_context.document_graph_validator
        document_entity_extractor = ctx.request_context.lifespan_context.document_entity_extractor

        if not document_graph_validator or not document_entity_extractor:
            return json.dumps({
                "success": False,
                "error": "GraphRAG components not available. Check Neo4j and OpenAI configuration."
            }, indent=2)

        # Step 1: Standard crawl with vector embeddings
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            return json.dumps({
                "success": False,
                "error": f"Failed to crawl URL: {result.error_message}"
            }, indent=2)

        # Extract source info
        parsed_url = urlparse(url)
        source_id = parsed_url.netloc or parsed_url.path

        # Step 2: Chunk content
        from utils import chunk_content
        chunks = chunk_content(result.markdown, max_chunk_size=chunk_size)

        # Step 3: Store in Supabase (vector embeddings)
        total_word_count = len(result.markdown.split())
        source_summary = extract_source_summary(source_id, result.markdown[:5000])
        update_source_info(supabase_client, source_id, source_summary, total_word_count)

        add_documents_to_supabase(
            supabase_client=supabase_client,
            chunks=[{"text": chunk, "url": url} for chunk in chunks],
            source_id=source_id
        )

        # Step 4: Extract entities and relationships
        extraction_result = await document_entity_extractor.extract_entities_from_chunks(
            chunks=chunks[:10],  # Limit to first 10 chunks for performance
            max_concurrent=3
        )

        if extraction_result.error:
            return json.dumps({
                "success": False,
                "error": f"Entity extraction failed: {extraction_result.error}",
                "crawl_success": True,
                "documents_stored": len(chunks)
            }, indent=2)

        # Step 5: Store document node in Neo4j
        # Generate document ID (use URL as identifier for now)
        import hashlib
        document_id = hashlib.md5(url.encode()).hexdigest()

        await document_graph_validator.store_document_node(
            document_id=document_id,
            source_id=source_id,
            url=url,
            title=result.markdown.split("\n")[0][:200] if result.markdown else "Untitled"
        )

        # Step 6: Store entities
        entities_stored = 0
        if extract_entities and extraction_result.entities:
            entities_dict = [
                {
                    "type": entity.type,
                    "name": entity.name,
                    "description": entity.description,
                    "mentions": entity.mentions
                }
                for entity in extraction_result.entities
            ]
            entities_stored = await document_graph_validator.store_entities(
                document_id=document_id,
                entities=entities_dict
            )

        # Step 7: Store relationships
        relationships_stored = 0
        if extract_relationships and extraction_result.relationships:
            relationships_dict = [
                {
                    "from_entity": rel.from_entity,
                    "to_entity": rel.to_entity,
                    "relationship_type": rel.relationship_type,
                    "description": rel.description,
                    "confidence": rel.confidence
                }
                for rel in extraction_result.relationships
            ]
            relationships_stored = await document_graph_validator.store_relationships(
                relationships=relationships_dict
            )

        return json.dumps({
            "success": True,
            "url": url,
            "source_id": source_id,
            "crawl_results": {
                "documents_stored": len(chunks),
                "total_words": total_word_count
            },
            "graph_extraction": {
                "entities_found": len(extraction_result.entities),
                "entities_stored": entities_stored,
                "relationships_found": len(extraction_result.relationships),
                "relationships_stored": relationships_stored,
                "extraction_time": f"{extraction_result.extraction_time:.2f}s"
            },
            "document_id": document_id
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }, indent=2)


@mcp.tool()
async def graphrag_query(
    ctx: Context,
    query: str,
    use_graph_enrichment: bool = True,
    max_entities: int = 15,
    source_filter: Optional[str] = None
) -> str:
    """
    Perform RAG query with optional graph enrichment for richer context.

    This tool combines vector similarity search (traditional RAG) with knowledge graph
    traversal (GraphRAG) to provide more comprehensive answers that understand
    entity relationships, dependencies, and connections.

    **When to use graph enrichment:**
    - Complex questions about how things relate
    - Questions about dependencies or prerequisites
    - Multi-hop reasoning questions
    - When you need to understand entity connections

    **When to disable graph enrichment (faster):**
    - Simple factual lookups
    - Time-sensitive queries
    - Very broad queries that don't need deep context

    Args:
        ctx: The MCP server provided context
        query: Search query
        use_graph_enrichment: Add graph context to results (default: True)
        max_entities: Maximum entities to include in graph enrichment (default: 15)
        source_filter: Optional source domain filter

    Returns:
        JSON string with:
        - Answer text with context
        - Source documents
        - Graph entities and relationships (if enrichment enabled)
        - Relevance scores

    Example:
        graphrag_query("How do I configure OAuth2 in FastAPI?", use_graph_enrichment=True)
    """
    try:
        supabase_client = ctx.request_context.lifespan_context.supabase_client
        document_graph_queries = ctx.request_context.lifespan_context.document_graph_queries

        # Step 1: Vector search (standard RAG)
        documents = search_documents(
            supabase_client=supabase_client,
            query=query,
            source_filter=source_filter,
            match_count=10
        )

        if not documents:
            return json.dumps({
                "success": True,
                "answer": "No relevant documents found for your query.",
                "documents": [],
                "graph_enrichment": None
            }, indent=2)

        # Step 2: Graph enrichment (if enabled and available)
        graph_context = None
        enrichment_text = ""

        if use_graph_enrichment and document_graph_queries:
            # Extract document IDs (would need to be stored in Supabase metadata)
            # For now, we'll use URLs as fallback
            doc_identifiers = [doc.get("url", "") for doc in documents[:5]]

            # This is a simplified version - in production you'd link Supabase IDs to Neo4j
            enrichment_text = "\n\n## Related Concepts and Dependencies\n\n"
            enrichment_text += "Graph enrichment is available. Connect Supabase document IDs to Neo4j for full GraphRAG capabilities.\n"

        # Step 3: Build context for LLM
        context_parts = []
        for i, doc in enumerate(documents[:5], 1):
            context_parts.append(f"**Source {i}:** {doc.get('url', 'Unknown')}")
            context_parts.append(doc.get('content', '')[:1000])
            context_parts.append("")

        context = "\n".join(context_parts)
        if enrichment_text:
            context = enrichment_text + "\n\n" + context

        # Step 4: Generate answer with LLM
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If graph enrichment is included, use it to provide more comprehensive answers that explain relationships and dependencies."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nProvide a detailed answer based on the context."}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return json.dumps({
            "success": True,
            "query": query,
            "answer": answer,
            "graph_enrichment_used": use_graph_enrichment and document_graph_queries is not None,
            "documents_found": len(documents),
            "sources": [
                {
                    "url": doc.get("url", "Unknown"),
                    "relevance": doc.get("similarity", 0)
                }
                for doc in documents[:5]
            ]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Query failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def query_document_graph(
    ctx: Context,
    cypher_query: str
) -> str:
    """
    Execute a custom Cypher query on the document knowledge graph.

    This tool provides direct access to the Neo4j document graph for advanced users
    who want to write custom graph queries.

    **Common query patterns:**

    Find all entities of a type:
    ```cypher
    MATCH (t:Technology)
    RETURN t.name, t.description
    LIMIT 10
    ```

    Find relationships:
    ```cypher
    MATCH (a)-[r:REQUIRES]->(b)
    RETURN a.name, type(r), b.name
    LIMIT 20
    ```

    Find entities mentioned in documents:
    ```cypher
    MATCH (d:Document)-[:MENTIONS]->(e)
    WHERE d.source_id = 'example.com'
    RETURN e.name, labels(e)[0] as type, count(*) as mentions
    ORDER BY mentions DESC
    ```

    Args:
        ctx: The MCP server provided context
        cypher_query: Cypher query string

    Returns:
        JSON string with query results

    Example:
        query_document_graph("MATCH (c:Concept) RETURN c.name LIMIT 10")
    """
    try:
        # Check if GraphRAG is enabled
        graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
        if not graphrag_enabled:
            return json.dumps({
                "success": False,
                "error": "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment."
            }, indent=2)

        document_graph_queries = ctx.request_context.lifespan_context.document_graph_queries

        if not document_graph_queries:
            return json.dumps({
                "success": False,
                "error": "Document graph queries not available. Check Neo4j configuration."
            }, indent=2)

        # Execute query
        result = await document_graph_queries.query_graph(cypher_query)

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Query execution failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def get_entity_context(
    ctx: Context,
    entity_name: str,
    max_hops: int = 2
) -> str:
    """
    Get comprehensive context for an entity from the knowledge graph.

    This tool retrieves an entity and its neighborhood in the graph, including:
    - Entity description and type
    - Related entities (connected nodes)
    - Relationships (edges)
    - Documents that mention the entity

    Useful for:
    - Understanding what an entity is and how it relates to other concepts
    - Finding all documents that discuss a specific technology or concept
    - Exploring entity neighborhoods
    - Building context for complex questions

    Args:
        ctx: The MCP server provided context
        entity_name: Name of entity to look up (e.g., "FastAPI", "OAuth2", "Docker")
        max_hops: Maximum relationship hops to traverse (default: 2)

    Returns:
        JSON string with:
        - Entity information
        - Related entities
        - Relationships
        - Documents mentioning the entity

    Example:
        get_entity_context("FastAPI", max_hops=2)
    """
    try:
        # Check if GraphRAG is enabled
        graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
        if not graphrag_enabled:
            return json.dumps({
                "success": False,
                "error": "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment."
            }, indent=2)

        document_graph_queries = ctx.request_context.lifespan_context.document_graph_queries

        if not document_graph_queries:
            return json.dumps({
                "success": False,
                "error": "Document graph queries not available. Check Neo4j configuration."
            }, indent=2)

        # Get entity context
        context = await document_graph_queries.get_entity_context(
            entity_name=entity_name,
            max_hops=max_hops
        )

        if not context:
            return json.dumps({
                "success": False,
                "error": f"Entity '{entity_name}' not found in knowledge graph."
            }, indent=2)

        return json.dumps({
            "success": True,
            "entity": {
                "name": context.entity_name,
                "type": context.entity_type,
                "description": context.description
            },
            "related_entities": [
                {
                    "name": rel["name"],
                    "type": rel["type"],
                    "relationship": rel["relationship"]
                }
                for rel in context.related_entities
            ],
            "relationships": [
                {
                    "from": rel["from"],
                    "to": rel["to"],
                    "type": rel["type"]
                }
                for rel in context.relationships
            ],
            "documents": [
                {
                    "id": doc["id"],
                    "url": doc["url"],
                    "title": doc["title"]
                }
                for doc in context.documents
            ],
            "stats": {
                "related_entities_count": len(context.related_entities),
                "relationships_count": len(context.relationships),
                "documents_count": len(context.documents)
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get entity context: {str(e)}"
        }, indent=2)


async def crawl_recursive_internal_links(
    crawler: AsyncWebCrawler,
    start_urls: List[str],
    max_depth: int = 3,
    max_concurrent: int = 10,
) -> List[Dict[str, Any]]:
    """
    Recursively crawl internal links from start URLs up to a maximum depth.

    Args:
        crawler: AsyncWebCrawler instance
        start_urls: List of starting URLs
        max_depth: Maximum recursion depth
        max_concurrent: Maximum number of concurrent browser sessions

    Returns:
        List of dictionaries with URL and markdown content
    """
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    visited = set()

    def normalize_url(url):
        return urldefrag(url)[0]

    current_urls = set([normalize_url(u) for u in start_urls])
    results_all = []

    for depth in range(max_depth):
        urls_to_crawl = [
            normalize_url(url)
            for url in current_urls
            if normalize_url(url) not in visited
        ]
        if not urls_to_crawl:
            break

        results = await crawler.arun_many(
            urls=urls_to_crawl, config=run_config, dispatcher=dispatcher
        )
        next_level_urls = set()

        for result in results:
            norm_url = normalize_url(result.url)
            visited.add(norm_url)

            if result.success and result.markdown:
                results_all.append({"url": result.url, "markdown": result.markdown})
                for link in result.links.get("internal", []):
                    next_url = normalize_url(link["href"])
                    if next_url not in visited:
                        next_level_urls.add(next_url)

        current_urls = next_level_urls

    return results_all


async def main():
    transport = os.getenv("TRANSPORT", "sse")

    # Add health check endpoint using FastMCP's custom_route decorator
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request):
        """Health check endpoint for monitoring and load balancers."""
        from starlette.responses import JSONResponse
        return JSONResponse({
            "status": "healthy",
            "service": "mcp-crawl4ai-rag",
            "version": "1.2.0",
            "transport": transport
        })

    if transport == "sse":
        # Run the MCP server with SSE transport
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "8051"))
        await mcp.run_async(transport="sse", host=host, port=port)
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
