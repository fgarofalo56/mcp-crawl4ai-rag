"""
Supabase Document Repository Implementation

Concrete implementation of DocumentRepository using Supabase.
"""

from __future__ import annotations

from supabase import Client

from ..utils import create_embeddings_batch, validate_url_safe
from .document_repository import Document, DocumentRepository


class SupabaseDocumentRepository(DocumentRepository):
    """
    Supabase implementation of DocumentRepository.

    Includes all the error handling, batching, and optimization
    from the original add_documents_to_supabase function.

    Example:
        client = create_supabase_client()
        repo = SupabaseDocumentRepository(client)

        documents = [
            Document(url="https://example.com", content="...", metadata={}, source_id="example.com")
        ]

        count = await repo.save_documents(documents)
        print(f"Saved {count} documents")
    """

    def __init__(self, client: Client, table_name: str = "crawled_pages"):
        """
        Initialize Supabase repository.

        Args:
            client: Supabase client instance
            table_name: Name of the table to use
        """
        self.client = client
        self.table_name = table_name

    async def save_documents(self, documents: list[Document], chunk_size: int = 5000) -> int:
        """
        Save documents to Supabase with proper chunking and batching.

        Includes:
        - URL validation (from Phase 1)
        - Batch deletion of existing records
        - Embedding creation
        - Batched insertion with retry logic

        Args:
            documents: List of documents to save
            chunk_size: Size for text chunking (unused here, handled upstream)

        Returns:
            Number of documents successfully saved
        """
        if not documents:
            return 0

        # Extract unique URLs and validate them
        unique_urls = list({doc.url for doc in documents})
        validated_urls = [url for url in unique_urls if validate_url_safe(url)]

        if len(validated_urls) != len(unique_urls):
            invalid_count = len(unique_urls) - len(validated_urls)
            print(f"⚠️  Skipped {invalid_count} invalid URLs")

        if not validated_urls:
            print("⚠️  No valid URLs to process")
            return 0

        # Delete existing records for validated URLs
        await self._delete_existing(validated_urls)

        # Create embeddings for all documents
        texts = [doc.content for doc in documents]
        embeddings = create_embeddings_batch(texts)

        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings, strict=False):
            doc.embedding = embedding

        # Insert in batches
        batch_size = 20
        total_inserted = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_data = [self._document_to_db_record(doc) for doc in batch]

            try:
                self.client.table(self.table_name).insert(batch_data).execute()
                total_inserted += len(batch)
            except Exception as e:
                print(f"⚠️  Batch insert failed: {e}")
                # Try individual inserts as fallback
                for doc_data in batch_data:
                    try:
                        self.client.table(self.table_name).insert([doc_data]).execute()
                        total_inserted += 1
                    except Exception as inner_e:
                        print(f"⚠️  Failed to insert document: {inner_e}")

        return total_inserted

    async def search_by_similarity(
        self, query_embedding: list[float], limit: int = 10, source_filter: str | None = None
    ) -> list[Document]:
        """Search using pgvector similarity."""
        # Implementation here
        # This would use the search_documents logic from utils.py
        pass

    async def delete_by_source(self, source_id: str) -> int:
        """Delete all documents from a source."""
        try:
            result = (
                self.client.table(self.table_name).delete().eq("source_id", source_id).execute()
            )
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"⚠️  Error deleting documents: {e}")
            return 0

    async def get_by_url(self, url: str) -> list[Document]:
        """Get all chunks for a URL."""
        try:
            result = self.client.table(self.table_name).select("*").eq("url", url).execute()
            return [self._db_record_to_document(record) for record in result.data]
        except Exception as e:
            print(f"⚠️  Error fetching documents: {e}")
            return []

    async def count_documents(self, source_filter: str | None = None) -> int:
        """Count documents."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact")
            if source_filter:
                query = query.eq("source_id", source_filter)
            result = query.execute()
            return result.count if hasattr(result, "count") else 0
        except Exception as e:
            print(f"⚠️  Error counting documents: {e}")
            return 0

    async def _delete_existing(self, urls: list[str]):
        """Delete existing records for URLs."""
        try:
            self.client.table(self.table_name).delete().in_("url", urls).execute()
            print("✓ Batch delete successful")
        except Exception as e:
            print(f"⚠️  Batch delete failed: {e}")
            # Fallback to individual deletion
            for url in urls:
                try:
                    self.client.table(self.table_name).delete().eq("url", url).execute()
                except Exception as inner_e:
                    print(f"⚠️  Error deleting URL {url}: {inner_e}")

    def _document_to_db_record(self, doc: Document) -> dict:
        """Convert domain model to database record."""
        return {
            "url": doc.url,
            "content": doc.content,
            "metadata": doc.metadata,
            "source_id": doc.source_id,
            "chunk_number": doc.chunk_number,
            "embedding": doc.embedding,
        }

    def _db_record_to_document(self, record: dict) -> Document:
        """Convert database record to domain model."""
        return Document(
            url=record.get("url", ""),
            content=record.get("content", ""),
            metadata=record.get("metadata", {}),
            source_id=record.get("source_id", ""),
            chunk_number=record.get("chunk_number", 0),
            embedding=record.get("embedding"),
        )
