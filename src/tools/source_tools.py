"""
Source Management Tools

MCP tools for managing data sources and retrieving available sources.
"""

import json

from fastmcp import Context

from utils import get_supabase_client


async def get_available_sources(ctx: Context) -> str:
    """
    Get a list of all available data sources that have been crawled and stored.

    This tool queries the database to find unique sources (domains) that have content
    stored, along with basic statistics about each source.

    Returns:
        JSON string containing:
        - List of available sources with their statistics
        - Total number of sources
        - Total documents across all sources

    Example:
        {
            "sources": [
                {
                    "source": "docs.python.org",
                    "document_count": 150,
                    "last_updated": "2024-01-15T10:30:00Z"
                }
            ],
            "total_sources": 1,
            "total_documents": 150
        }
    """
    try:
        supabase_client = get_supabase_client()

        # Query to get unique sources with counts
        response = supabase_client.table("crawled_pages").select("url, metadata").execute()

        if not response.data:
            return json.dumps(
                {
                    "sources": [],
                    "total_sources": 0,
                    "total_documents": 0,
                    "message": "No sources found in database",
                },
                indent=2,
            )

        # Extract sources (domains) from URLs
        sources_map = {}
        for doc in response.data:
            url = doc.get("url", "")
            if url:
                from urllib.parse import urlparse

                domain = urlparse(url).netloc
                if domain:
                    if domain not in sources_map:
                        sources_map[domain] = {"source": domain, "document_count": 0, "urls": set()}
                    sources_map[domain]["document_count"] += 1
                    sources_map[domain]["urls"].add(url)

        # Convert to list and add URL diversity metric
        sources_list = []
        for domain, data in sources_map.items():
            sources_list.append(
                {
                    "source": data["source"],
                    "document_count": data["document_count"],
                    "unique_urls": len(data["urls"]),
                }
            )

        # Sort by document count (descending)
        sources_list.sort(key=lambda x: x["document_count"], reverse=True)

        result = {
            "sources": sources_list,
            "total_sources": len(sources_list),
            "total_documents": sum(s["document_count"] for s in sources_list),
            "message": f"Found {len(sources_list)} unique sources",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve sources: {str(e)}",
                "sources": [],
                "total_sources": 0,
                "total_documents": 0,
            },
            indent=2,
        )


__all__ = ["get_available_sources"]
