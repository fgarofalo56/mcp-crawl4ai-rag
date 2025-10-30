"""
Repository Pattern - Document Repository

Abstract repository interface for document storage.
Implementations can use different backends (Supabase, PostgreSQL, SQLite, etc.)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Document:
    """Domain model for a document."""

    url: str
    content: str
    metadata: dict[str, Any]
    source_id: str
    chunk_number: int = 0
    embedding: list[float] | None = None


class DocumentRepository(ABC):
    """
    Abstract repository for document storage.

    This interface allows swapping database backends without changing business logic.

    Benefits:
    - Easy to mock for testing
    - Can add caching layer transparently
    - Can switch from Supabase to PostgreSQL without changing services
    - All database logic centralized

    Example:
        # In production
        repo = SupabaseDocumentRepository(supabase_client)

        # In tests
        repo = InMemoryDocumentRepository()

        # In development
        repo = SQLiteDocumentRepository("dev.db")

        # All use the same interface!
        await repo.save_documents(documents)
    """

    @abstractmethod
    async def save_documents(self, documents: list[Document], chunk_size: int = 5000) -> int:
        """
        Save documents to storage.

        Args:
            documents: List of documents to save
            chunk_size: Size for text chunking

        Returns:
            Number of documents successfully saved
        """
        pass

    @abstractmethod
    async def search_by_similarity(
        self, query_embedding: list[float], limit: int = 10, source_filter: str | None = None
    ) -> list[Document]:
        """
        Search documents by vector similarity.

        Args:
            query_embedding: Embedding vector to search for
            limit: Maximum number of results
            source_filter: Optional filter by source

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    async def delete_by_source(self, source_id: str) -> int:
        """
        Delete all documents from a source.

        Args:
            source_id: Source identifier

        Returns:
            Number of documents deleted
        """
        pass

    @abstractmethod
    async def get_by_url(self, url: str) -> list[Document]:
        """
        Get all chunks for a specific URL.

        Args:
            url: URL to search for

        Returns:
            List of document chunks for that URL
        """
        pass

    @abstractmethod
    async def count_documents(self, source_filter: str | None = None) -> int:
        """
        Count documents in storage.

        Args:
            source_filter: Optional filter by source

        Returns:
            Number of documents
        """
        pass


class CodeExampleRepository(ABC):
    """Repository for code examples."""

    @abstractmethod
    async def save_code_examples(self, examples: list[CodeExample]) -> int:
        """Save code examples."""
        pass

    @abstractmethod
    async def search_code_examples(
        self, query_embedding: list[float], limit: int = 10, language_filter: str | None = None
    ) -> list[CodeExample]:
        """Search code examples by similarity."""
        pass
