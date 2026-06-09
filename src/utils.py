"""
Utility functions for the Crawl4AI MCP server.
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import sys
import time
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import AzureOpenAI
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# Normalize and fix Azure OpenAI endpoint
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
deployment = os.getenv("DEPLOYMENT_NAME", "o4-mini")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")
apiversion = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Initialize Azure OpenAI client with latest SDK pattern
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=subscription_key,
    api_version=apiversion,
)

# Get deployment names from environment
model = os.getenv("OPENAI_MODEL", "")
deployment = os.getenv("DEPLOYMENT", "")
embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

# Embedding batch configuration
MAX_BATCH_SIZE = 16  # Azure OpenAI limit for embeddings
MAX_TOKENS_PER_BATCH = 8000  # Conservative limit (Azure allows more but this is safer)
RATE_LIMIT_DELAY = 0.1  # 100ms between batches


def count_tokens_estimate(text: str) -> int:
    """
    Estimate token count for text (rough estimate: 1 token ≈ 4 characters).

    For production, consider using tiktoken for accurate counts.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    return len(text) // 4


def batch_texts_by_tokens(
    texts: list[str], max_tokens: int = MAX_TOKENS_PER_BATCH
) -> list[list[str]]:
    """
    Split texts into token-aware batches.

    Args:
        texts: List of texts to batch
        max_tokens: Maximum tokens per batch

    Returns:
        List of text batches
    """
    if not texts:
        return []

    batches = []
    current_batch = []
    current_tokens = 0

    for text in texts:
        # Estimate tokens for this text
        text_tokens = count_tokens_estimate(text)

        # Truncate if single text is too large
        if text_tokens > max_tokens:
            # Roughly keep max_tokens worth of characters
            max_chars = max_tokens * 4
            text = text[:max_chars]
            text_tokens = max_tokens

        # Check if adding this text would exceed limits
        if current_tokens + text_tokens > max_tokens or len(current_batch) >= MAX_BATCH_SIZE:
            if current_batch:
                batches.append(current_batch)
            current_batch = [text]
            current_tokens = text_tokens
        else:
            current_batch.append(text)
            current_tokens += text_tokens

    # Add remaining batch
    if current_batch:
        batches.append(current_batch)

    return batches


def get_supabase_client() -> Client:
    """
    Get a Supabase client with the URL and key from environment variables.

    Returns:
        Supabase client instance
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    print(f"Connecting to Supabase at: {url}", file=sys.stderr, flush=True)

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )

    return create_client(url, key)


def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Create embeddings for multiple texts with intelligent batching and rate limiting.

    Features:
    - Token-aware batching to stay within API limits
    - Automatic batch size validation
    - Rate limiting between batches
    - Retry logic with exponential backoff
    - Graceful degradation to individual embeddings on failure

    Args:
        texts: List of texts to create embeddings for

    Returns:
        List of embeddings (each embedding is a list of floats)
    """
    if not texts:
        return []

    print(f"Creating embeddings for {len(texts)} texts...", file=sys.stderr, flush=True)

    # Split into safe batches
    batches = batch_texts_by_tokens(texts, MAX_TOKENS_PER_BATCH)
    print(f"Split into {len(batches)} batches for processing", file=sys.stderr, flush=True)

    all_embeddings = []
    max_retries = 3

    for batch_idx, batch in enumerate(batches):
        # Rate limiting between batches (skip first batch)
        if batch_idx > 0:
            time.sleep(RATE_LIMIT_DELAY)

        retry_delay = 1.0  # Start with 1 second delay

        for retry in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=embedding_deployment,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                print(
                    f"✓ Batch {batch_idx + 1}/{len(batches)} complete ({len(batch)} texts)",
                    file=sys.stderr,
                    flush=True,
                )
                break  # Success, move to next batch

            except Exception as e:
                error_str = str(e).lower()

                if retry < max_retries - 1:
                    # Determine wait time based on error type
                    if "rate_limit" in error_str or "429" in error_str:
                        wait_time = (2**retry) * 2  # 2s, 4s, 8s for rate limits
                        print(
                            f"⚠️  Rate limited on batch {batch_idx + 1}, waiting {wait_time}s...",
                            file=sys.stderr,
                            flush=True,
                        )
                    else:
                        wait_time = retry_delay
                        print(
                            f"⚠️  Error on batch {batch_idx + 1} (attempt {retry + 1}/{max_retries}): {e}",
                            file=sys.stderr,
                            flush=True,
                        )
                        print(f"Retrying in {wait_time}s...", file=sys.stderr, flush=True)

                    time.sleep(wait_time)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # All retries exhausted, try individual embeddings as fallback
                    print(
                        f"⚠️  Failed to create batch embeddings after {max_retries} attempts: {e}",
                        file=sys.stderr,
                        flush=True,
                    )
                    print(
                        f"Attempting to create {len(batch)} embeddings individually...",
                        file=sys.stderr,
                        flush=True,
                    )

                    individual_embeddings = []
                    successful_count = 0

                    for i, text in enumerate(batch):
                        try:
                            individual_response = client.embeddings.create(
                                model=embedding_deployment, input=[text]
                            )
                            individual_embeddings.append(individual_response.data[0].embedding)
                            successful_count += 1
                        except Exception as individual_error:
                            print(
                                f"⚠️  Failed embedding {i + 1}/{len(batch)}: {individual_error}",
                                file=sys.stderr,
                                flush=True,
                            )
                            # Add zero embedding as fallback
                            individual_embeddings.append([0.0] * 1536)

                    all_embeddings.extend(individual_embeddings)
                    print(
                        f"Created {successful_count}/{len(batch)} embeddings individually",
                        file=sys.stderr,
                        flush=True,
                    )
                    break

    print(f"✓ Total embeddings created: {len(all_embeddings)}", file=sys.stderr, flush=True)
    return all_embeddings


def create_embedding(text: str) -> list[float]:
    """
    Create an embedding for a single text using OpenAI's API.

    Args:
        text: Text to create an embedding for

    Returns:
        List of floats representing the embedding
    """
    try:
        embeddings = create_embeddings_batch([text])
        return embeddings[0] if embeddings else [0.0] * 1536
    except Exception as e:
        print(f"Error creating embedding: {e}", file=sys.stderr, flush=True)
        # Return empty embedding if there's an error
        return [0.0] * 1536


def generate_contextual_embedding(full_document: str, chunk: str) -> tuple[str, bool]:
    """
    Generate contextual information for a chunk within a document to improve retrieval.

    Args:
        full_document: The complete document text
        chunk: The specific chunk of text to generate context for

    Returns:
        Tuple containing:
        - The contextual text that situates the chunk within the document
        - Boolean indicating if contextual embedding was performed
    """
    model_choice = os.getenv("MODEL_CHOICE")

    try:
        # Create the prompt for generating contextual information
        prompt = f"""<document>
{full_document[:25000]}
</document>
Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""

        # Call the OpenAI API to generate contextual information
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise contextual information.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_completion_tokens=200,
        )

        # Extract the generated context
        context = response.choices[0].message.content.strip()

        # Combine the context with the original chunk
        contextual_text = f"{context}\n---\n{chunk}"

        return contextual_text, True

    except Exception as e:
        print(
            f"Error generating contextual embedding: {e}. Using original chunk instead.",
            file=sys.stderr,
            flush=True,
        )
        return chunk, False


def process_chunk_with_context(args: tuple[str, str, str]) -> tuple[str, bool]:
    """
    Process a single chunk with contextual embedding.
    This function is designed to be used with concurrent.futures.

    Args:
        args: Tuple containing (url, content, full_document)

    Returns:
        Tuple containing:
        - The contextual text that situates the chunk within the document
        - Boolean indicating if contextual embedding was performed
    """
    url, content, full_document = args
    return generate_contextual_embedding(full_document, content)


def validate_url_safe(url: str) -> bool:
    """
    Validate URL is safe for database operations.

    Checks for:
    - Valid URL format
    - Allowed schemes (http, https, ftp)
    - No SQL injection patterns
    - No suspicious characters

    Args:
        url: URL to validate

    Returns:
        True if URL is safe, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # Check length (prevent extremely long URLs)
    if len(url) > 2048:
        return False

    try:
        parsed = urlparse(url)

        # Check for valid scheme
        if parsed.scheme not in ["http", "https", "ftp"]:
            return False

        # Must have a network location (domain)
        if not parsed.netloc:
            return False

        # Check for SQL-like patterns that might be injection attempts
        sql_patterns = [
            "'",
            '"',
            ";",
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "union",
            "select",
            "drop",
            "insert",
        ]
        url_lower = url.lower()
        for pattern in sql_patterns:
            if pattern in url_lower:
                # Allow these patterns in actual content, but be suspicious of them in URL structure
                # Check if they appear in suspicious contexts
                if pattern in parsed.netloc.lower() or pattern in parsed.path.lower():
                    return False

        return True

    except Exception as e:
        print(f"⚠️  URL validation error for '{url}': {e}", file=sys.stderr, flush=True)
        return False


def _validate_and_filter_urls(urls: list[str]) -> list[str]:
    """
    Validate URLs and filter out invalid ones.

    Args:
        urls: List of URLs to validate

    Returns:
        List of validated URLs
    """
    unique_urls = list(set(urls))
    validated_urls = [url for url in unique_urls if validate_url_safe(url)]

    if len(validated_urls) != len(unique_urls):
        invalid_count = len(unique_urls) - len(validated_urls)
        invalid_urls = [url for url in unique_urls if url not in validated_urls]
        print(f"⚠️  Skipped {invalid_count} invalid URLs:", file=sys.stderr, flush=True)
        for invalid_url in invalid_urls[:5]:  # Show first 5
            print(f"   - {invalid_url[:100]}...", file=sys.stderr, flush=True)
        if len(invalid_urls) > 5:
            print(f"   - ... and {len(invalid_urls) - 5} more", file=sys.stderr, flush=True)

    return validated_urls


def _delete_existing_records_batch(client: Client, validated_urls: list[str]) -> None:
    """
    Delete existing records for URLs with batch deletion and fallback.

    Args:
        client: Supabase client
        validated_urls: List of validated URLs to delete records for
    """
    try:
        if validated_urls:
            print(
                f"Deleting existing records for {len(validated_urls)} validated URLs...",
                file=sys.stderr,
                flush=True,
            )
            client.table("crawled_pages").delete().in_("url", validated_urls).execute()
            print("✓ Batch delete successful", file=sys.stderr, flush=True)
    except Exception as e:
        print(
            f"⚠️  Batch delete failed: {e}. Trying one-by-one deletion as fallback.",
            file=sys.stderr,
            flush=True,
        )
        # Fallback: delete records one by one
        for url in validated_urls:
            try:
                client.table("crawled_pages").delete().eq("url", url).execute()
            except Exception as inner_e:
                print(
                    f"⚠️  Error deleting record for URL {url}: {inner_e}",
                    file=sys.stderr,
                    flush=True,
                )


def _apply_contextual_embeddings(
    batch_contents: list[str],
    batch_urls: list[str],
    batch_metadatas: list[dict[str, Any]],
    url_to_full_document: dict[str, str],
) -> list[str]:
    """
    Apply contextual embeddings to batch contents in parallel.

    Args:
        batch_contents: List of content chunks
        batch_urls: List of URLs for each chunk
        batch_metadatas: List of metadata for each chunk (modified in-place)
        url_to_full_document: Mapping of URLs to full documents

    Returns:
        List of contextual contents (or original if processing fails)
    """
    # Prepare arguments for parallel processing
    process_args = []
    for j, content in enumerate(batch_contents):
        url = batch_urls[j]
        full_document = url_to_full_document.get(url, "")
        process_args.append((url, content, full_document))

    # Process in parallel using ThreadPoolExecutor
    contextual_contents = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks and collect results
        future_to_idx = {
            executor.submit(process_chunk_with_context, arg): idx
            for idx, arg in enumerate(process_args)
        }

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result, success = future.result()
                contextual_contents.append(result)
                if success:
                    batch_metadatas[idx]["contextual_embedding"] = True
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}", file=sys.stderr, flush=True)
                contextual_contents.append(batch_contents[idx])

    # Validate results
    if len(contextual_contents) != len(batch_contents):
        print(
            f"Warning: Expected {len(batch_contents)} results but got {len(contextual_contents)}",
            file=sys.stderr,
            flush=True,
        )
        return batch_contents

    return contextual_contents


def _prepare_batch_data(
    contextual_contents: list[str],
    batch_urls: list[str],
    batch_chunk_numbers: list[int],
    batch_metadatas: list[dict[str, Any]],
    batch_embeddings: list[list[float]],
) -> list[dict[str, Any]]:
    """
    Prepare batch data for Supabase insertion.

    Args:
        contextual_contents: List of content chunks
        batch_urls: List of URLs
        batch_chunk_numbers: List of chunk numbers
        batch_metadatas: List of metadata dictionaries
        batch_embeddings: List of embedding vectors

    Returns:
        List of data dictionaries ready for insertion
    """
    batch_data = []
    for j in range(len(contextual_contents)):
        chunk_size = len(contextual_contents[j])
        parsed_url = urlparse(batch_urls[j])
        source_id = parsed_url.netloc or parsed_url.path

        data = {
            "url": batch_urls[j],
            "chunk_number": batch_chunk_numbers[j],
            "content": contextual_contents[j],
            "metadata": {"chunk_size": chunk_size, **batch_metadatas[j]},
            "source_id": source_id,
            "embedding": batch_embeddings[j],
        }
        batch_data.append(data)

    return batch_data


def _insert_batch_with_retry(
    client: Client, batch_data: list[dict[str, Any]], max_retries: int = 3
) -> None:
    """
    Insert batch data into Supabase with retry logic and fallback.

    Args:
        client: Supabase client
        batch_data: List of data dictionaries to insert
        max_retries: Maximum number of retry attempts
    """
    retry_delay = 1.0

    for retry in range(max_retries):
        try:
            client.table("crawled_pages").insert(batch_data).execute()
            break  # Success
        except Exception as e:
            if retry < max_retries - 1:
                print(
                    f"Error inserting batch (attempt {retry + 1}/{max_retries}): {e}",
                    file=sys.stderr,
                    flush=True,
                )
                print(f"Retrying in {retry_delay} seconds...", file=sys.stderr, flush=True)
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                # Final attempt failed - try individual inserts
                print(
                    f"Failed to insert batch after {max_retries} attempts: {e}",
                    file=sys.stderr,
                    flush=True,
                )
                print("Attempting to insert records individually...", file=sys.stderr, flush=True)

                successful_inserts = 0
                for record in batch_data:
                    try:
                        client.table("crawled_pages").insert(record).execute()
                        successful_inserts += 1
                    except Exception as individual_error:
                        print(
                            f"Failed to insert record for URL {record['url']}: {individual_error}",
                            file=sys.stderr,
                            flush=True,
                        )

                if successful_inserts > 0:
                    print(
                        f"Successfully inserted {successful_inserts}/{len(batch_data)} records individually",
                        file=sys.stderr,
                        flush=True,
                    )


def add_documents_to_supabase(
    client: Client,
    urls: list[str],
    chunk_numbers: list[int],
    contents: list[str],
    metadatas: list[dict[str, Any]],
    url_to_full_document: dict[str, str],
    batch_size: int = 20,
) -> None:
    """
    Add documents to the Supabase crawled_pages table in batches.
    Deletes existing records with the same URLs before inserting to prevent duplicates.

    Features:
    - URL validation before database operations
    - Safe batch deletion with fallback
    - Contextual embeddings support

    Args:
        client: Supabase client
        urls: List of URLs
        chunk_numbers: List of chunk numbers
        contents: List of document contents
        metadatas: List of document metadata
        url_to_full_document: Dictionary mapping URLs to their full document content
        batch_size: Size of each batch for insertion
    """
    # Validate URLs
    validated_urls = _validate_and_filter_urls(urls)
    if not validated_urls:
        print("⚠️  No valid URLs to process", file=sys.stderr, flush=True)
        return

    # Delete existing records
    _delete_existing_records_batch(client, validated_urls)

    # Check contextual embeddings setting
    use_contextual_embeddings = os.getenv("USE_CONTEXTUAL_EMBEDDINGS", "false") == "true"
    print(
        f"\n\nUse contextual embeddings: {use_contextual_embeddings}\n\n",
        file=sys.stderr,
        flush=True,
    )

    # Process in batches
    for i in range(0, len(contents), batch_size):
        batch_end = min(i + batch_size, len(contents))

        # Extract batch slices
        batch_urls = urls[i:batch_end]
        batch_chunk_numbers = chunk_numbers[i:batch_end]
        batch_contents = contents[i:batch_end]
        batch_metadatas = metadatas[i:batch_end]

        # Apply contextual embeddings if enabled
        if use_contextual_embeddings:
            contextual_contents = _apply_contextual_embeddings(
                batch_contents, batch_urls, batch_metadatas, url_to_full_document
            )
        else:
            contextual_contents = batch_contents

        # Create embeddings and prepare data
        batch_embeddings = create_embeddings_batch(contextual_contents)
        batch_data = _prepare_batch_data(
            contextual_contents,
            batch_urls,
            batch_chunk_numbers,
            batch_metadatas,
            batch_embeddings,
        )

        # Insert with retry logic
        _insert_batch_with_retry(client, batch_data)


def search_documents(
    client: Client,
    query: str,
    match_count: int = 10,
    filter_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Search for documents in Supabase using vector similarity.

    Args:
        client: Supabase client
        query: Query text
        match_count: Maximum number of results to return
        filter_metadata: Optional metadata filter

    Returns:
        List of matching documents
    """
    # Create embedding for the query
    query_embedding = create_embedding(query)

    # Execute the search using the match_crawled_pages function
    try:
        # Only include filter parameter if filter_metadata is provided and not empty
        params = {"query_embedding": query_embedding, "match_count": match_count}

        # Only add the filter if it's actually provided and not empty
        if filter_metadata:
            params["filter"] = filter_metadata  # Pass the dictionary directly, not JSON-encoded

        result = client.rpc("match_crawled_pages", params).execute()

        return result.data
    except Exception as e:
        print(f"Error searching documents: {e}", file=sys.stderr, flush=True)
        return []


def extract_code_blocks(markdown_content: str, min_length: int = 1000) -> list[dict[str, Any]]:
    """
    Extract code blocks from markdown content along with context.

    Args:
        markdown_content: The markdown content to extract code blocks from
        min_length: Minimum length of code blocks to extract (default: 1000 characters)

    Returns:
        List of dictionaries containing code blocks and their context
    """
    code_blocks = []

    # Skip if content starts with triple backticks (edge case for files wrapped in backticks)
    content = markdown_content.strip()
    start_offset = 0
    if content.startswith("```"):
        # Skip the first triple backticks
        start_offset = 3
        print("Skipping initial triple backticks", file=sys.stderr, flush=True)

    # Find all occurrences of triple backticks
    backtick_positions = []
    pos = start_offset
    while True:
        pos = markdown_content.find("```", pos)
        if pos == -1:
            break
        backtick_positions.append(pos)
        pos += 3

    # Process pairs of backticks
    i = 0
    while i < len(backtick_positions) - 1:
        start_pos = backtick_positions[i]
        end_pos = backtick_positions[i + 1]

        # Extract the content between backticks
        code_section = markdown_content[start_pos + 3 : end_pos]

        # Check if there's a language specifier on the first line
        lines = code_section.split("\n", 1)
        if len(lines) > 1:
            # Check if first line is a language specifier (no spaces, common language names)
            first_line = lines[0].strip()
            if first_line and " " not in first_line and len(first_line) < 20:
                language = first_line
                code_content = lines[1].strip() if len(lines) > 1 else ""
            else:
                language = ""
                code_content = code_section.strip()
        else:
            language = ""
            code_content = code_section.strip()

        # Skip if code block is too short
        if len(code_content) < min_length:
            i += 2  # Move to next pair
            continue

        # Extract context before (1000 chars)
        context_start = max(0, start_pos - 1000)
        context_before = markdown_content[context_start:start_pos].strip()

        # Extract context after (1000 chars)
        context_end = min(len(markdown_content), end_pos + 3 + 1000)
        context_after = markdown_content[end_pos + 3 : context_end].strip()

        code_blocks.append(
            {
                "code": code_content,
                "language": language,
                "context_before": context_before,
                "context_after": context_after,
                "full_context": f"{context_before}\n\n{code_content}\n\n{context_after}",
            }
        )

        # Move to next pair (skip the closing backtick we just processed)
        i += 2

    return code_blocks


def generate_code_example_summary(code: str, context_before: str, context_after: str) -> str:
    """
    Generate a summary for a code example using its surrounding context.

    Args:
        code: The code example
        context_before: Context before the code
        context_after: Context after the code

    Returns:
        A summary of what the code example demonstrates
    """
    model_choice = os.getenv("MODEL_CHOICE")

    # Create the prompt
    prompt = f"""<context_before>
{context_before[-500:] if len(context_before) > 500 else context_before}
</context_before>

<code_example>
{code[:1500] if len(code) > 1500 else code}
</code_example>

<context_after>
{context_after[:500] if len(context_after) > 500 else context_after}
</context_after>

Based on the code example and its surrounding context, provide a concise summary (2-3 sentences) that describes what this code example demonstrates and its purpose. Focus on the practical application and key concepts illustrated.
"""

    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise code example summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_completion_tokens=100,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating code example summary: {e}", file=sys.stderr, flush=True)
        return "Code example for demonstration purposes."


def add_code_examples_to_supabase(
    client: Client,
    urls: list[str],
    chunk_numbers: list[int],
    code_examples: list[str],
    summaries: list[str],
    metadatas: list[dict[str, Any]],
    batch_size: int = 20,
) -> None:
    """
    Add code examples to the Supabase code_examples table in batches.

    Args:
        client: Supabase client
        urls: List of URLs
        chunk_numbers: List of chunk numbers
        code_examples: List of code example contents
        summaries: List of code example summaries
        metadatas: List of metadata dictionaries
        batch_size: Size of each batch for insertion
    """
    if not urls:
        return

    # Delete existing records for these URLs
    unique_urls = list(set(urls))
    for url in unique_urls:
        try:
            client.table("code_examples").delete().eq("url", url).execute()
        except Exception as e:
            print(
                f"Error deleting existing code examples for {url}: {e}", file=sys.stderr, flush=True
            )

    # Process in batches
    total_items = len(urls)
    for i in range(0, total_items, batch_size):
        batch_end = min(i + batch_size, total_items)
        batch_texts = []

        # Create combined texts for embedding (code + summary)
        for j in range(i, batch_end):
            combined_text = f"{code_examples[j]}\n\nSummary: {summaries[j]}"
            batch_texts.append(combined_text)

        # Create embeddings for the batch
        embeddings = create_embeddings_batch(batch_texts)

        # Check if embeddings are valid (not all zeros)
        valid_embeddings = []
        for embedding in embeddings:
            if embedding and not all(v == 0.0 for v in embedding):
                valid_embeddings.append(embedding)
            else:
                print(
                    "Warning: Zero or invalid embedding detected, creating new one...",
                    file=sys.stderr,
                    flush=True,
                )
                # Try to create a single embedding as fallback
                single_embedding = create_embedding(batch_texts[len(valid_embeddings)])
                valid_embeddings.append(single_embedding)

        # Prepare batch data
        batch_data = []
        for j, embedding in enumerate(valid_embeddings):
            idx = i + j

            # Extract source_id from URL
            parsed_url = urlparse(urls[idx])
            source_id = parsed_url.netloc or parsed_url.path

            batch_data.append(
                {
                    "url": urls[idx],
                    "chunk_number": chunk_numbers[idx],
                    "content": code_examples[idx],
                    "summary": summaries[idx],
                    "metadata": metadatas[idx],  # Store as JSON object, not string
                    "source_id": source_id,
                    "embedding": embedding,
                }
            )

        # Insert batch into Supabase with retry logic
        max_retries = 3
        retry_delay = 1.0  # Start with 1 second delay

        for retry in range(max_retries):
            try:
                client.table("code_examples").insert(batch_data).execute()
                # Success - break out of retry loop
                break
            except Exception as e:
                if retry < max_retries - 1:
                    print(
                        f"Error inserting batch into Supabase (attempt {retry + 1}/{max_retries}): {e}",
                        file=sys.stderr,
                        flush=True,
                    )
                    print(f"Retrying in {retry_delay} seconds...", file=sys.stderr, flush=True)
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Final attempt failed
                    print(
                        f"Failed to insert batch after {max_retries} attempts: {e}",
                        file=sys.stderr,
                        flush=True,
                    )
                    # Optionally, try inserting records one by one as a last resort
                    print(
                        "Attempting to insert records individually...", file=sys.stderr, flush=True
                    )
                    successful_inserts = 0
                    for record in batch_data:
                        try:
                            client.table("code_examples").insert(record).execute()
                            successful_inserts += 1
                        except Exception as individual_error:
                            print(
                                f"Failed to insert individual record for URL {record['url']}: {individual_error}",
                                file=sys.stderr,
                                flush=True,
                            )

                    if successful_inserts > 0:
                        print(
                            f"Successfully inserted {successful_inserts}/{len(batch_data)} records individually",
                            file=sys.stderr,
                            flush=True,
                        )
        print(
            f"Inserted batch {i//batch_size + 1} of {(total_items + batch_size - 1)//batch_size} code examples",
            file=sys.stderr,
            flush=True,
        )


def update_source_info(client: Client, source_id: str, summary: str, word_count: int) -> None:
    """
    Update or insert source information in the sources table.

    Args:
        client: Supabase client
        source_id: The source ID (domain)
        summary: Summary of the source
        word_count: Total word count for the source
    """
    try:
        # Try to update existing source
        result = (
            client.table("sources")
            .update(
                {
                    "summary": summary,
                    "total_word_count": word_count,
                    "updated_at": "now()",
                }
            )
            .eq("source_id", source_id)
            .execute()
        )

        # If no rows were updated, insert new source
        if not result.data:
            client.table("sources").insert(
                {
                    "source_id": source_id,
                    "summary": summary,
                    "total_word_count": word_count,
                }
            ).execute()
            print(f"Created new source: {source_id}", file=sys.stderr, flush=True)
        else:
            print(f"Updated source: {source_id}", file=sys.stderr, flush=True)

    except Exception as e:
        print(f"Error updating source {source_id}: {e}", file=sys.stderr, flush=True)


def extract_source_summary(source_id: str, content: str, max_length: int = 500) -> str:
    """
    Extract a summary for a source from its content using an LLM.

    This function uses the OpenAI API to generate a concise summary of the source content.

    Args:
        source_id: The source ID (domain)
        content: The content to extract a summary from
        max_length: Maximum length of the summary

    Returns:
        A summary string
    """
    # Default summary if we can't extract anything meaningful
    default_summary = f"Content from {source_id}"

    if not content or len(content.strip()) == 0:
        return default_summary

    # Get the model choice from environment variables
    model_choice = os.getenv("MODEL_CHOICE")

    # Limit content length to avoid token limits
    truncated_content = content[:25000] if len(content) > 25000 else content

    # Create the prompt for generating the summary
    prompt = f"""<source_content>
{truncated_content}
</source_content>

The above content is from the documentation for '{source_id}'. Please provide a concise summary (3-5 sentences) that describes what this library/tool/framework is about. The summary should help understand what the library/tool/framework accomplishes and the purpose.
"""

    try:
        # Call the OpenAI API to generate the summary
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise library/tool/framework summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_completion_tokens=150,
        )

        # Extract the generated summary
        summary = response.choices[0].message.content.strip()

        # Ensure the summary is not too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    except Exception as e:
        print(
            f"Error generating summary with LLM for {source_id}: {e}. Using default summary.",
            file=sys.stderr,
            flush=True,
        )
        return default_summary


def search_code_examples(
    client: Client,
    query: str,
    match_count: int = 10,
    filter_metadata: dict[str, Any] | None = None,
    source_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search for code examples in Supabase using vector similarity.

    Args:
        client: Supabase client
        query: Query text
        match_count: Maximum number of results to return
        filter_metadata: Optional metadata filter
        source_id: Optional source ID to filter results

    Returns:
        List of matching code examples
    """
    # Create a more descriptive query for better embedding match
    # Since code examples are embedded with their summaries, we should make the query more descriptive
    enhanced_query = f"Code example for {query}\n\nSummary: Example code showing {query}"

    # Create embedding for the enhanced query
    query_embedding = create_embedding(enhanced_query)

    # Execute the search using the match_code_examples function
    try:
        # Only include filter parameter if filter_metadata is provided and not empty
        params = {"query_embedding": query_embedding, "match_count": match_count}

        # Only add the filter if it's actually provided and not empty
        if filter_metadata:
            params["filter"] = filter_metadata

        # Add source filter if provided
        if source_id:
            params["source_filter"] = source_id

        result = client.rpc("match_code_examples", params).execute()

        return result.data
    except Exception as e:
        print(f"Error searching code examples: {e}", file=sys.stderr, flush=True)
    return []


def chunk_content(
    content: str,
    max_chunk_size: int = 1500,
    min_chunk_size: int = 400,
) -> list[str]:
    """Split text into retrieval-friendly chunks."""

    if not content:
        return []

    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be positive")

    min_chunk_size = max(0, min(min_chunk_size, max_chunk_size))

    normalized = content.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    paragraphs = [
        segment.strip() for segment in re.split(r"\n\s*\n", normalized) if segment.strip()
    ]

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    def flush_current() -> None:
        nonlocal current, current_length
        if not current:
            return
        chunk_text = "\n\n".join(current).strip()
        if chunk_text:
            chunks.append(chunk_text)
        current = []
        current_length = 0

    for para in paragraphs:
        para_len = len(para)

        if para_len > max_chunk_size:
            flush_current()
            for start in range(0, para_len, max_chunk_size):
                segment = para[start : start + max_chunk_size].strip()
                if segment:
                    chunks.append(segment)
            continue

        prospective = current_length + (2 if current else 0) + para_len
        if prospective <= max_chunk_size:
            if current:
                current_length += 2 + para_len
            else:
                current_length = para_len
            current.append(para)
            continue

        flush_current()
        current.append(para)
        current_length = para_len

    flush_current()

    if len(chunks) >= 2 and len(chunks[-1]) < min_chunk_size:
        chunks[-2] = f"{chunks[-2]}\n\n{chunks[-1]}".strip()
        chunks.pop()

    return chunks
