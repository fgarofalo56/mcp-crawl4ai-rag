"""
Document Knowledge Graph Validator

Initializes and manages Neo4j schema for document knowledge graph (GraphRAG).
Separate from code repository graph - this is for web content entities and relationships.
"""

import asyncio
import logging
import socket
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Patch for Windows compatibility with Neo4j
if not hasattr(socket, 'EAI_ADDRFAMILY'):
    socket.EAI_ADDRFAMILY = -9

from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)


@dataclass
class DocumentGraphStats:
    """Statistics about document knowledge graph"""
    total_documents: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    entity_types: Dict[str, int] = field(default_factory=dict)
    relationship_types: Dict[str, int] = field(default_factory=dict)


class DocumentGraphValidator:
    """
    Manages Neo4j schema for document knowledge graph.

    Schema Overview:
    - Document nodes linked to Supabase IDs
    - Entity nodes (Concept, Technology, Configuration, Person, Organization, etc.)
    - Relationship edges between entities
    - Source nodes for content organization
    """

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None

    async def initialize(self):
        """Initialize Neo4j connection and create document graph schema"""
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

        # Create schema
        await self._create_schema()

        logger.info("Document knowledge graph validator initialized")

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()

    async def _create_schema(self):
        """Create constraints and indexes for document graph"""
        schema_queries = [
            # Document nodes (linked to Supabase)
            "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE INDEX document_source IF NOT EXISTS FOR (d:Document) ON (d.source_id)",
            "CREATE INDEX document_url IF NOT EXISTS FOR (d:Document) ON (d.url)",

            # Entity nodes - Concepts
            "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            "CREATE INDEX concept_type IF NOT EXISTS FOR (c:Concept) ON (c.type)",

            # Entity nodes - Technologies
            "CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
            "CREATE INDEX technology_category IF NOT EXISTS FOR (t:Technology) ON (t.category)",

            # Entity nodes - Configurations
            "CREATE CONSTRAINT config_name IF NOT EXISTS FOR (c:Configuration) REQUIRE c.name IS UNIQUE",

            # Entity nodes - People
            "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",

            # Entity nodes - Organizations
            "CREATE CONSTRAINT org_name IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE",

            # Entity nodes - Products/Tools
            "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",

            # Source nodes (for organization)
            "CREATE CONSTRAINT source_id IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE",
        ]

        async with self.driver.session() as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                    logger.debug(f"Executed schema query: {query[:50]}...")
                except Exception as e:
                    # Ignore if constraint/index already exists
                    if "already exists" not in str(e).lower() and "equivalent" not in str(e).lower():
                        logger.warning(f"Schema creation warning: {e}")

    async def store_document_node(
        self,
        document_id: str,
        source_id: str,
        url: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create or update a Document node linked to Supabase.

        Args:
            document_id: Unique ID from Supabase crawled_pages table
            source_id: Source domain/identifier
            url: Original URL of the document
            title: Optional document title
            metadata: Optional additional metadata

        Returns:
            True if successful
        """
        query = """
        MERGE (d:Document {id: $document_id})
        SET d.source_id = $source_id,
            d.url = $url,
            d.title = $title,
            d.updated_at = datetime(),
            d.metadata = $metadata

        MERGE (s:Source {id: $source_id})
        MERGE (d)-[:FROM_SOURCE]->(s)

        RETURN d.id as doc_id
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    document_id=document_id,
                    source_id=source_id,
                    url=url,
                    title=title or "Untitled",
                    metadata=metadata or {}
                )
                record = await result.single()
                return record is not None
        except Exception as e:
            logger.error(f"Error storing document node: {e}")
            return False

    async def store_entities(
        self,
        document_id: str,
        entities: List[Dict[str, Any]]
    ) -> int:
        """
        Store extracted entities and link them to document.

        Args:
            document_id: Document ID from Supabase
            entities: List of entity dicts with keys: type, name, description, mentions

        Returns:
            Number of entities stored
        """
        stored_count = 0

        for entity in entities:
            entity_type = entity.get("type", "Concept")
            entity_name = entity.get("name")
            entity_description = entity.get("description", "")
            mentions = entity.get("mentions", 1)

            if not entity_name:
                continue

            # Map entity types to Neo4j labels
            label_map = {
                "Concept": "Concept",
                "Technology": "Technology",
                "Configuration": "Configuration",
                "Person": "Person",
                "Organization": "Organization",
                "Product": "Product",
                "Tool": "Technology",  # Map Tool to Technology
                "Framework": "Technology",
                "Library": "Technology",
            }

            label = label_map.get(entity_type, "Concept")

            query = f"""
            MERGE (e:{label} {{name: $name}})
            SET e.description = COALESCE(e.description, $description),
                e.type = $entity_type,
                e.updated_at = datetime()

            MATCH (d:Document {{id: $document_id}})
            MERGE (d)-[m:MENTIONS]->(e)
            SET m.count = COALESCE(m.count, 0) + $mentions,
                m.updated_at = datetime()

            RETURN e.name as entity_name
            """

            try:
                async with self.driver.session() as session:
                    result = await session.run(
                        query,
                        name=entity_name,
                        description=entity_description,
                        entity_type=entity_type,
                        document_id=document_id,
                        mentions=mentions
                    )
                    record = await result.single()
                    if record:
                        stored_count += 1
            except Exception as e:
                logger.error(f"Error storing entity {entity_name}: {e}")

        return stored_count

    async def store_relationships(
        self,
        relationships: List[Dict[str, Any]]
    ) -> int:
        """
        Store relationships between entities.

        Args:
            relationships: List of relationship dicts with keys: from_entity, to_entity,
                          relationship_type, description, confidence

        Returns:
            Number of relationships stored
        """
        stored_count = 0

        for rel in relationships:
            from_entity = rel.get("from_entity")
            to_entity = rel.get("to_entity")
            rel_type = rel.get("relationship_type", "RELATED_TO")
            description = rel.get("description", "")
            confidence = rel.get("confidence", 0.8)

            if not from_entity or not to_entity:
                continue

            # Sanitize relationship type for Cypher (must be valid identifier)
            rel_type = rel_type.upper().replace(" ", "_").replace("-", "_")

            # Valid relationship types
            valid_types = [
                "RELATED_TO", "REQUIRES", "DEPENDS_ON", "USES", "IMPLEMENTS",
                "EXTENDS", "PART_OF", "CONFIGURES", "ENABLES", "PROVIDES",
                "ALTERNATIVE_TO", "SIMILAR_TO", "PREREQUISITE_FOR", "DOCUMENTED_IN"
            ]

            if rel_type not in valid_types:
                rel_type = "RELATED_TO"

            query = f"""
            MATCH (from {{name: $from_entity}})
            MATCH (to {{name: $to_entity}})
            MERGE (from)-[r:{rel_type}]->(to)
            SET r.description = $description,
                r.confidence = $confidence,
                r.updated_at = datetime()
            RETURN type(r) as rel_type
            """

            try:
                async with self.driver.session() as session:
                    result = await session.run(
                        query,
                        from_entity=from_entity,
                        to_entity=to_entity,
                        description=description,
                        confidence=confidence
                    )
                    record = await result.single()
                    if record:
                        stored_count += 1
            except Exception as e:
                logger.error(f"Error storing relationship {from_entity}->{to_entity}: {e}")

        return stored_count

    async def get_document_graph_stats(self) -> DocumentGraphStats:
        """Get statistics about the document knowledge graph"""
        stats = DocumentGraphStats()

        queries = {
            "documents": "MATCH (d:Document) RETURN count(d) as count",
            "entities": "MATCH (n) WHERE n:Concept OR n:Technology OR n:Configuration OR n:Person OR n:Organization OR n:Product RETURN count(n) as count",
            "relationships": "MATCH ()-[r]->() WHERE NOT type(r) IN ['MENTIONS', 'FROM_SOURCE'] RETURN count(r) as count",
            "entity_types": """
                MATCH (n)
                WHERE n:Concept OR n:Technology OR n:Configuration OR n:Person OR n:Organization OR n:Product
                RETURN labels(n)[0] as type, count(*) as count
            """,
            "relationship_types": """
                MATCH ()-[r]->()
                WHERE NOT type(r) IN ['MENTIONS', 'FROM_SOURCE']
                RETURN type(r) as type, count(*) as count
            """
        }

        try:
            async with self.driver.session() as session:
                # Total counts
                result = await session.run(queries["documents"])
                record = await result.single()
                stats.total_documents = record["count"] if record else 0

                result = await session.run(queries["entities"])
                record = await result.single()
                stats.total_entities = record["count"] if record else 0

                result = await session.run(queries["relationships"])
                record = await result.single()
                stats.total_relationships = record["count"] if record else 0

                # Entity types breakdown
                result = await session.run(queries["entity_types"])
                async for record in result:
                    stats.entity_types[record["type"]] = record["count"]

                # Relationship types breakdown
                result = await session.run(queries["relationship_types"])
                async for record in result:
                    stats.relationship_types[record["type"]] = record["count"]

        except Exception as e:
            logger.error(f"Error getting document graph stats: {e}")

        return stats

    async def clear_document_graph(self, source_id: Optional[str] = None) -> Dict[str, int]:
        """
        Clear document graph data (for testing/reset).

        Args:
            source_id: If provided, only clear data for this source

        Returns:
            Dict with counts of deleted nodes and relationships
        """
        if source_id:
            query = """
            MATCH (d:Document {source_id: $source_id})
            OPTIONAL MATCH (d)-[r]-()
            DELETE r, d
            RETURN count(d) as deleted_docs
            """
            params = {"source_id": source_id}
        else:
            query = """
            MATCH (n)
            WHERE n:Document OR n:Concept OR n:Technology OR n:Configuration OR n:Person OR n:Organization OR n:Product OR n:Source
            OPTIONAL MATCH (n)-[r]-()
            DELETE r, n
            RETURN count(n) as deleted_nodes
            """
            params = {}

        try:
            async with self.driver.session() as session:
                result = await session.run(query, **params)
                record = await result.single()

                if source_id:
                    return {"deleted_documents": record["deleted_docs"] if record else 0}
                else:
                    return {"deleted_nodes": record["deleted_nodes"] if record else 0}
        except Exception as e:
            logger.error(f"Error clearing document graph: {e}")
            return {"error": str(e)}
