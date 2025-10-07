"""
Document Graph Query Functions

Provides query capabilities for the document knowledge graph,
enabling graph-enriched RAG and entity exploration.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)


@dataclass
class EntityContext:
    """Context information about an entity from the graph"""
    entity_name: str
    entity_type: str
    description: str = ""
    related_entities: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GraphEnrichmentResult:
    """Results from graph enrichment for RAG"""
    document_ids: List[str]
    entity_contexts: List[EntityContext] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    dependencies: List[Tuple[str, str]] = field(default_factory=list)  # (entity, requires)
    enrichment_text: str = ""  # Formatted text for LLM context


class DocumentGraphQueries:
    """
    Query functions for document knowledge graph.

    Supports graph traversal, entity context retrieval, and
    graph-enriched RAG queries.
    """

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None

    async def initialize(self):
        """Initialize Neo4j connection"""
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        logger.info("Document graph queries initialized")

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()

    async def get_entity_context(
        self,
        entity_name: str,
        max_hops: int = 2,
        max_related: int = 10
    ) -> Optional[EntityContext]:
        """
        Get comprehensive context for an entity.

        Args:
            entity_name: Name of entity to look up
            max_hops: Maximum relationship hops to traverse
            max_related: Maximum related entities to return

        Returns:
            EntityContext with related entities, documents, and relationships
        """
        query = """
        MATCH (e {name: $entity_name})
        OPTIONAL MATCH (e)<-[:MENTIONS]-(d:Document)
        OPTIONAL MATCH (e)-[r]-(related)
        WHERE related:Concept OR related:Technology OR related:Configuration OR related:Person OR related:Organization OR related:Product

        WITH e,
             collect(DISTINCT {id: d.id, url: d.url, title: d.title}) as docs,
             collect(DISTINCT {
                 name: related.name,
                 type: labels(related)[0],
                 relationship: type(r),
                 description: related.description
             })[0..$max_related] as related_entities,
             collect(DISTINCT {
                 from: startNode(r).name,
                 to: endNode(r).name,
                 type: type(r),
                 description: r.description
             })[0..20] as relationships

        RETURN
            e.name as name,
            labels(e)[0] as type,
            e.description as description,
            docs,
            related_entities,
            relationships
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    entity_name=entity_name,
                    max_related=max_related
                )
                record = await result.single()

                if not record:
                    return None

                context = EntityContext(
                    entity_name=record["name"],
                    entity_type=record["type"],
                    description=record.get("description", ""),
                    documents=[doc for doc in record["docs"] if doc.get("id")],
                    related_entities=[rel for rel in record["related_entities"] if rel.get("name")],
                    relationships=[rel for rel in record["relationships"] if rel.get("from")]
                )

                return context

        except Exception as e:
            logger.error(f"Error getting entity context for {entity_name}: {e}")
            return None

    async def enrich_documents_with_graph(
        self,
        document_ids: List[str],
        max_entities: int = 20
    ) -> GraphEnrichmentResult:
        """
        Enrich document results with graph context for RAG.

        This is the core of GraphRAG: take vector search results (document IDs)
        and add graph-based context (entities, relationships, dependencies).

        Args:
            document_ids: List of document IDs from vector search
            max_entities: Maximum entities to include in enrichment

        Returns:
            GraphEnrichmentResult with enriched context
        """
        result = GraphEnrichmentResult(document_ids=document_ids)

        if not document_ids:
            return result

        query = """
        MATCH (d:Document)
        WHERE d.id IN $document_ids
        MATCH (d)-[:MENTIONS]->(e)
        WHERE e:Concept OR e:Technology OR e:Configuration OR e:Person OR e:Organization OR e:Product

        // Get related entities (1-hop)
        OPTIONAL MATCH (e)-[r]-(related)
        WHERE related:Concept OR related:Technology OR related:Configuration OR related:Person OR related:Organization OR related:Product

        WITH e,
             count(DISTINCT d) as doc_count,
             collect(DISTINCT {
                 name: related.name,
                 type: labels(related)[0],
                 relationship: type(r)
             }) as related_entities,
             collect(DISTINCT {from: startNode(r).name, to: endNode(r).name, type: type(r)}) as relationships

        ORDER BY doc_count DESC
        LIMIT $max_entities

        RETURN
            e.name as entity_name,
            labels(e)[0] as entity_type,
            e.description as description,
            related_entities,
            relationships
        """

        try:
            async with self.driver.session() as session:
                query_result = await session.run(
                    query,
                    document_ids=document_ids,
                    max_entities=max_entities
                )

                enrichment_parts = []

                async for record in query_result:
                    entity_name = record["entity_name"]
                    entity_type = record["entity_type"]
                    description = record.get("description", "")

                    # Build entity context
                    context = EntityContext(
                        entity_name=entity_name,
                        entity_type=entity_type,
                        description=description,
                        related_entities=[r for r in record["related_entities"] if r.get("name")],
                        relationships=[r for r in record["relationships"] if r.get("from")]
                    )
                    result.entity_contexts.append(context)

                    # Track concepts for summary
                    if entity_type == "Concept":
                        result.related_concepts.append(entity_name)

                    # Track dependencies
                    for rel in context.relationships:
                        if rel.get("type") in ["REQUIRES", "DEPENDS_ON", "PREREQUISITE_FOR"]:
                            result.dependencies.append((rel["from"], rel["to"]))

                    # Build enrichment text
                    enrichment_parts.append(f"\n**{entity_name}** ({entity_type})")
                    if description:
                        enrichment_parts.append(f"  {description}")

                    if context.related_entities:
                        related_names = [r["name"] for r in context.related_entities[:5]]
                        enrichment_parts.append(f"  Related: {', '.join(related_names)}")

                    if context.relationships:
                        for rel in context.relationships[:3]:
                            rel_desc = f"  - {rel['from']} {rel['type']} {rel['to']}"
                            enrichment_parts.append(rel_desc)

                # Format enrichment text
                if enrichment_parts:
                    result.enrichment_text = (
                        "## Knowledge Graph Context\n\n"
                        "The following entities and relationships were found in the knowledge graph:\n"
                        + "\n".join(enrichment_parts)
                        + "\n"
                    )

        except Exception as e:
            logger.error(f"Error enriching documents with graph: {e}")

        return result

    async def query_graph(self, cypher_query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a custom Cypher query on the document graph.

        Args:
            cypher_query: Cypher query string
            parameters: Optional query parameters

        Returns:
            Dict with results and metadata
        """
        if parameters is None:
            parameters = {}

        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, **parameters)

                records = []
                async for record in result:
                    records.append(dict(record))

                return {
                    "success": True,
                    "record_count": len(records),
                    "records": records
                }

        except Exception as e:
            logger.error(f"Error executing graph query: {e}")
            return {
                "success": False,
                "error": str(e),
                "records": []
            }

    async def find_related_documents(
        self,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find documents related to an entity through graph traversal.

        Args:
            entity_name: Starting entity name
            max_hops: Maximum relationship hops
            limit: Maximum documents to return

        Returns:
            List of document dicts with relevance scores
        """
        query = f"""
        MATCH (e {{name: $entity_name}})
        MATCH path = (e)-[*1..{max_hops}]-(related)
        MATCH (related)<-[:MENTIONS]-(d:Document)

        WITH d,
             length(path) as distance,
             count(DISTINCT related) as entity_count

        RETURN DISTINCT
            d.id as document_id,
            d.url as url,
            d.title as title,
            d.source_id as source_id,
            distance,
            entity_count,
            (1.0 / distance) * entity_count as relevance_score

        ORDER BY relevance_score DESC
        LIMIT $limit
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    entity_name=entity_name,
                    limit=limit
                )

                documents = []
                async for record in result:
                    documents.append({
                        "document_id": record["document_id"],
                        "url": record["url"],
                        "title": record["title"],
                        "source_id": record["source_id"],
                        "distance": record["distance"],
                        "entity_count": record["entity_count"],
                        "relevance_score": record["relevance_score"]
                    })

                return documents

        except Exception as e:
            logger.error(f"Error finding related documents for {entity_name}: {e}")
            return []

    async def find_entity_paths(
        self,
        from_entity: str,
        to_entity: str,
        max_length: int = 5
    ) -> List[List[str]]:
        """
        Find paths between two entities in the graph.

        Args:
            from_entity: Starting entity name
            to_entity: Target entity name
            max_length: Maximum path length

        Returns:
            List of paths (each path is a list of entity names)
        """
        query = f"""
        MATCH path = shortestPath(
            (from {{name: $from_entity}})-[*1..{max_length}]-(to {{name: $to_entity}})
        )

        WITH path,
             [node in nodes(path) | node.name] as node_names,
             [rel in relationships(path) | type(rel)] as rel_types

        RETURN node_names, rel_types
        LIMIT 10
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    from_entity=from_entity,
                    to_entity=to_entity
                )

                paths = []
                async for record in result:
                    node_names = record["node_names"]
                    rel_types = record["rel_types"]

                    # Format path with relationships
                    path_parts = []
                    for i, node in enumerate(node_names):
                        path_parts.append(node)
                        if i < len(rel_types):
                            path_parts.append(f"--[{rel_types[i]}]-->")

                    paths.append(path_parts)

                return paths

        except Exception as e:
            logger.error(f"Error finding paths from {from_entity} to {to_entity}: {e}")
            return []

    async def get_entity_neighborhood(
        self,
        entity_name: str,
        radius: int = 1
    ) -> Dict[str, Any]:
        """
        Get the local neighborhood of an entity.

        Args:
            entity_name: Entity to explore
            radius: How many hops to include

        Returns:
            Dict with nodes and edges in the neighborhood
        """
        query = f"""
        MATCH (center {{name: $entity_name}})
        MATCH path = (center)-[*1..{radius}]-(neighbor)
        WHERE neighbor:Concept OR neighbor:Technology OR neighbor:Configuration OR neighbor:Person OR neighbor:Organization OR neighbor:Product

        WITH center, collect(DISTINCT neighbor) as neighbors, collect(DISTINCT path) as paths

        UNWIND paths as p
        UNWIND relationships(p) as r

        RETURN
            center.name as center_name,
            labels(center)[0] as center_type,
            collect(DISTINCT {{
                name: startNode(r).name,
                type: labels(startNode(r))[0]
            }}) + collect(DISTINCT {{
                name: endNode(r).name,
                type: labels(endNode(r))[0]
            }}) as nodes,
            collect(DISTINCT {{
                from: startNode(r).name,
                to: endNode(r).name,
                type: type(r)
            }}) as edges
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, entity_name=entity_name)
                record = await result.single()

                if not record:
                    return {"nodes": [], "edges": []}

                # Deduplicate nodes
                nodes_dict = {node["name"]: node for node in record["nodes"]}
                nodes = list(nodes_dict.values())

                return {
                    "center": {
                        "name": record["center_name"],
                        "type": record["center_type"]
                    },
                    "nodes": nodes,
                    "edges": record["edges"]
                }

        except Exception as e:
            logger.error(f"Error getting neighborhood for {entity_name}: {e}")
            return {"nodes": [], "edges": []}
