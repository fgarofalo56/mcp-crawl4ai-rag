"""
Helper functions for web crawling operations.

This module provides focused helper functions for crawling operations,
extracted from crawl_single_page for improved modularity and testability.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import os
from typing import Any
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from supabase import Client

# Import chunking and metadata extraction from crawling_utils
from .crawling_utils import extract_section_info, smart_chunk_markdown

# Import utility functions
from .utils import (
    add_code_examples_to_supabase,
    add_documents_to_supabase,
    extract_code_blocks,
    extract_source_summary,
    generate_code_example_summary,
    update_source_info,
)


def validate_crawl_url(url: str) -> dict[str, Any]:
    """
    Validate a URL for crawling.

    Args:
        url: URL to validate

    Returns:
        Dict with 'valid' boolean and optional 'error' message
    """
    if not url or not isinstance(url, str):
        return {"valid": False, "error": "URL is required and must be a string"}

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return {"valid": False, "error": "URL must start with http:// or https://"}

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return {"valid": False, "error": "Invalid URL format"}
        return {"valid": True, "source_id": parsed.netloc or parsed.path}
    except Exception as e:
        return {"valid": False, "error": f"Invalid URL: {str(e)}"}


async def crawl_and_extract_content(
    crawler: AsyncWebCrawler, url: str
) -> tuple[bool, str, dict[str, Any]]:
    """
    Crawl a URL and extract its content.

    Args:
        crawler: AsyncWebCrawler instance
        url: URL to crawl

    Returns:
        Tuple of (success, markdown_content, metadata)
    """
    try:
        # Configure the crawl
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)

        # Crawl the page
        result = await crawler.arun(url=url, config=run_config)

        if result.success and result.markdown:
            metadata = {
                "success": True,
                "content_length": len(result.markdown),
                "links": {
                    "internal": len(result.links.get("internal", [])),
                    "external": len(result.links.get("external", [])),
                },
            }
            return True, result.markdown, metadata
        else:
            return False, "", {"error": result.error_message}

    except Exception as e:
        return False, "", {"error": str(e)}


def chunk_and_prepare_documents(
    url: str, markdown_content: str, source_id: str, chunk_size: int = 5000
) -> tuple[list[str], list[int], list[str], list[dict[str, Any]], int]:
    """
    Chunk content and prepare document data for storage.

    Args:
        url: Source URL
        markdown_content: Markdown content to chunk
        source_id: Source identifier
        chunk_size: Maximum size of each chunk

    Returns:
        Tuple of (urls, chunk_numbers, contents, metadatas, total_word_count)
    """
    chunks = smart_chunk_markdown(markdown_content, chunk_size)

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

    return urls, chunk_numbers, contents, metadatas, total_word_count


def process_code_example_wrapper(args: tuple[str, str, str]) -> str:
    """
    Process a single code example to generate its summary.
    Wrapper function for concurrent processing.

    Args:
        args: Tuple containing (code, context_before, context_after)

    Returns:
        The generated summary
    """
    code, context_before, context_after = args
    return generate_code_example_summary(code, context_before, context_after)


def extract_and_process_code_examples(
    url: str, markdown_content: str, source_id: str, max_workers: int = 10
) -> tuple[list[str], list[int], list[str], list[str], list[dict[str, Any]]]:
    """
    Extract and process code examples from markdown content.

    Args:
        url: Source URL
        markdown_content: Markdown content to extract code from
        source_id: Source identifier
        max_workers: Maximum number of parallel workers

    Returns:
        Tuple of (urls, chunk_numbers, code_examples, summaries, metadatas)
    """
    code_blocks = extract_code_blocks(markdown_content)

    if not code_blocks:
        return [], [], [], [], []

    code_urls = []
    code_chunk_numbers = []
    code_examples = []
    code_summaries = []
    code_metadatas = []

    # Process code examples in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Prepare arguments for parallel processing
        summary_args = [
            (block["code"], block["context_before"], block["context_after"])
            for block in code_blocks
        ]

        # Generate summaries in parallel
        summaries = list(executor.map(process_code_example_wrapper, summary_args))

    # Prepare code example data
    for i, (block, summary) in enumerate(zip(code_blocks, summaries, strict=False)):
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

    return code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas


def store_crawl_results(
    supabase_client: Client,
    urls: list[str],
    chunk_numbers: list[int],
    contents: list[str],
    metadatas: list[dict[str, Any]],
    url_to_full_document: dict[str, str],
    source_id: str,
    total_word_count: int,
    source_summary: str,
) -> None:
    """
    Store crawl results in Supabase.

    Args:
        supabase_client: Supabase client instance
        urls: List of URLs
        chunk_numbers: List of chunk numbers
        contents: List of content chunks
        metadatas: List of metadata dicts
        url_to_full_document: Mapping of URL to full document
        source_id: Source identifier
        total_word_count: Total word count for the source
        source_summary: Summary of the source content
    """
    # Update source information FIRST (before inserting documents)
    update_source_info(supabase_client, source_id, source_summary, total_word_count)

    # Add documentation chunks to Supabase (AFTER source exists)
    add_documents_to_supabase(
        supabase_client,
        urls,
        chunk_numbers,
        contents,
        metadatas,
        url_to_full_document,
    )


def store_code_examples(
    supabase_client: Client,
    code_urls: list[str],
    code_chunk_numbers: list[int],
    code_examples: list[str],
    code_summaries: list[str],
    code_metadatas: list[dict[str, Any]],
) -> None:
    """
    Store code examples in Supabase.

    Args:
        supabase_client: Supabase client instance
        code_urls: List of URLs
        code_chunk_numbers: List of chunk numbers
        code_examples: List of code examples
        code_summaries: List of code summaries
        code_metadatas: List of metadata dicts
    """
    if code_examples:
        add_code_examples_to_supabase(
            supabase_client,
            code_urls,
            code_chunk_numbers,
            code_examples,
            code_summaries,
            code_metadatas,
        )


def should_extract_code_examples() -> bool:
    """
    Check if code example extraction is enabled.

    Returns:
        True if code extraction is enabled, False otherwise
    """
    return os.getenv("USE_AGENTIC_RAG", "false") == "true"


def process_documentation_chunks(
    crawl_results: list[dict[str, Any]],
    chunk_size: int = 5000,
) -> tuple[
    list[str],
    list[int],
    list[str],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, str],
    dict[str, int],
    int,
]:
    """
    Process crawl results into chunks for storage.

    Args:
        crawl_results: List of crawled documents with 'url' and 'markdown' keys
        chunk_size: Size of chunks for splitting content

    Returns:
        Tuple of (urls, chunk_numbers, contents, metadatas, url_to_full_document,
                 source_content_map, source_word_counts, chunk_count)
    """
    urls = []
    chunk_numbers = []
    contents = []
    metadatas = []
    chunk_count = 0

    # Track sources and their content
    source_content_map = {}
    source_word_counts = {}
    url_to_full_document = {}

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
            source_content_map[source_id] = md[:5000]
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
            metadatas.append(meta)

            # Accumulate word count
            source_word_counts[source_id] += meta.get("word_count", 0)
            chunk_count += 1

        # Store full document
        url_to_full_document[source_url] = md

    return (
        urls,
        chunk_numbers,
        contents,
        metadatas,
        url_to_full_document,
        source_content_map,
        source_word_counts,
        chunk_count,
    )


def update_sources_parallel(
    supabase_client: Client,
    source_content_map: dict[str, str],
    source_word_counts: dict[str, int],
    max_workers: int = 5,
) -> None:
    """
    Update source information in parallel using ThreadPoolExecutor.

    Args:
        supabase_client: Supabase client instance
        source_content_map: Mapping of source_id to content sample
        source_word_counts: Mapping of source_id to total word count
        max_workers: Maximum number of parallel workers
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        source_summary_args = list(source_content_map.items())
        source_summaries = list(
            executor.map(
                lambda args: extract_source_summary(args[0], args[1]),
                source_summary_args,
            )
        )

    for (source_id, _), summary in zip(source_summary_args, source_summaries, strict=False):
        word_count = source_word_counts.get(source_id, 0)
        update_source_info(supabase_client, source_id, summary, word_count)


def extract_code_examples_from_documents(
    crawl_results: list[dict[str, Any]], max_workers: int = 10
) -> tuple[list[str], list[int], list[str], list[str], list[dict[str, Any]]]:
    """
    Extract and process code examples from all crawled documents.

    Args:
        crawl_results: List of crawled documents with 'url' and 'markdown' keys
        max_workers: Maximum number of parallel workers for code processing

    Returns:
        Tuple of (code_urls, code_chunk_numbers, code_examples,
                 code_summaries, code_metadatas)
    """
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

        if not code_blocks:
            continue

        # Process code examples in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            summary_args = [
                (block["code"], block["context_before"], block["context_after"])
                for block in code_blocks
            ]
            summaries = list(executor.map(process_code_example_wrapper, summary_args))

        # Prepare code example data
        parsed_url = urlparse(source_url)
        source_id = parsed_url.netloc or parsed_url.path

        for _i, (block, summary) in enumerate(zip(code_blocks, summaries, strict=False)):
            code_urls.append(source_url)
            code_chunk_numbers.append(len(code_examples))
            code_examples.append(block["code"])
            code_summaries.append(summary)

            code_meta = {
                "chunk_index": len(code_examples) - 1,
                "url": source_url,
                "source": source_id,
                "char_count": len(block["code"]),
                "word_count": len(block["code"].split()),
            }
            code_metadatas.append(code_meta)

    return (code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas)
