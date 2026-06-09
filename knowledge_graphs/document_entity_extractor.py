"""
Document Entity Extractor

Extracts entities and relationships from web documents using LLM analysis.
Creates structured knowledge graph data from unstructured text.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
    AsyncAzureOpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """An entity extracted from document text"""

    name: str
    type: str  # Concept, Technology, Configuration, Person, Organization, Product
    description: str = ""
    mentions: int = 1
    confidence: float = 0.8


@dataclass
class ExtractedRelationship:
    """A relationship between two entities"""

    from_entity: str
    to_entity: str
    relationship_type: str  # REQUIRES, USES, PART_OF, etc.
    description: str = ""
    confidence: float = 0.8


@dataclass
class ExtractionResult:
    """Results from entity extraction"""

    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)
    extraction_time: float = 0.0
    error: str | None = None


class DocumentEntityExtractor:
    """
    Extracts entities and relationships from documents using LLM.

    This is the core of GraphRAG - converting unstructured web content
    into structured graph data that can be queried and traversed.
    """

    # System prompt for entity extraction
    ENTITY_EXTRACTION_PROMPT = """You are an expert at extracting structured knowledge from technical documentation.

Analyze the following text and extract:

1. **Entities**: Important concepts, technologies, configurations, people, organizations, and products
2. **Relationships**: How these entities relate to each other

**Entity Types:**
- Concept: Abstract ideas, principles, patterns (e.g., "OAuth2", "Microservices")
- Technology: Programming languages, frameworks, tools (e.g., "Python", "FastAPI", "Docker")
- Configuration: Settings, environment variables, parameters (e.g., "PORT", "API_KEY")
- Person: Named individuals mentioned
- Organization: Companies, projects, teams
- Product: Software products, services

**Relationship Types:**
- REQUIRES: Entity A requires entity B to function
- USES: Entity A uses entity B
- PART_OF: Entity A is part of entity B
- IMPLEMENTS: Entity A implements entity B
- CONFIGURES: Entity A configures entity B
- ENABLES: Entity A enables entity B
- ALTERNATIVE_TO: Entity A is an alternative to entity B
- PREREQUISITE_FOR: Entity A is a prerequisite for entity B
- DOCUMENTED_IN: Entity A is documented in entity B

**Output Format (JSON):**
```json
{
  "entities": [
    {
      "name": "FastAPI",
      "type": "Technology",
      "description": "Modern Python web framework",
      "mentions": 5
    }
  ],
  "relationships": [
    {
      "from_entity": "FastAPI",
      "to_entity": "Python",
      "relationship_type": "USES",
      "description": "FastAPI is built with Python"
    }
  ]
}
```

**Guidelines:**
- Extract only the most important entities (5-20 per document chunk)
- Focus on entities that would help answer questions about the content
- Include relationships that show dependencies, hierarchies, and connections
- Use consistent naming (e.g., always "FastAPI" not "fastapi" or "Fast API")
- Avoid extracting overly generic entities like "code", "file", "system"

**Text to analyze:**
"""

    def __init__(
        self,
        openai_api_key: str | None = None,
        azure_openai_endpoint: str | None = None,
        azure_openai_key: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize entity extractor.

        Args:
            openai_api_key: OpenAI API key (for standard OpenAI)
            azure_openai_endpoint: Azure OpenAI endpoint (for Azure)
            azure_openai_key: Azure OpenAI API key
            model: Model to use for extraction (default: gpt-4o-mini for cost efficiency)
        """
        self.model = model

        if not AsyncOpenAI:
            raise ImportError("openai package is required for entity extraction")

        # Initialize OpenAI client (Azure or standard)
        if azure_openai_endpoint and azure_openai_key:
            # Use Azure-specific client
            if not AsyncAzureOpenAI:
                raise ImportError("openai package with Azure support required")

            self.client = AsyncAzureOpenAI(
                api_key=azure_openai_key,
                azure_endpoint=azure_openai_endpoint,
                api_version="2024-10-01-preview",
            )
            self.is_azure = True
        elif openai_api_key:
            self.client = AsyncOpenAI(api_key=openai_api_key)
            self.is_azure = False
        else:
            raise ValueError("Either openai_api_key or azure_openai_endpoint+key must be provided")

    async def extract_entities_from_text(
        self, text: str, max_length: int = 8000
    ) -> ExtractionResult:
        """
        Extract entities and relationships from text.

        Args:
            text: Text content to analyze (typically a document chunk)
            max_length: Maximum text length to process (truncate if longer)

        Returns:
            ExtractionResult with entities and relationships
        """
        import time

        start_time = time.time()

        # Truncate text if too long
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Text truncated...]"

        result = ExtractionResult()

        try:
            # Call LLM for extraction
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.ENTITY_EXTRACTION_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"},  # Request JSON output
            )

            # Parse response
            content = response.choices[0].message.content
            extracted = json.loads(content)

            # Convert to dataclass objects
            for entity_data in extracted.get("entities", []):
                entity = ExtractedEntity(
                    name=entity_data.get("name", ""),
                    type=entity_data.get("type", "Concept"),
                    description=entity_data.get("description", ""),
                    mentions=entity_data.get("mentions", 1),
                    confidence=entity_data.get("confidence", 0.8),
                )
                if entity.name:  # Only add if name is present
                    result.entities.append(entity)

            for rel_data in extracted.get("relationships", []):
                relationship = ExtractedRelationship(
                    from_entity=rel_data.get("from_entity", ""),
                    to_entity=rel_data.get("to_entity", ""),
                    relationship_type=rel_data.get("relationship_type", "RELATED_TO"),
                    description=rel_data.get("description", ""),
                    confidence=rel_data.get("confidence", 0.8),
                )
                if relationship.from_entity and relationship.to_entity:
                    result.relationships.append(relationship)

            result.extraction_time = time.time() - start_time

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            result.error = f"JSON parsing error: {e}"
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            result.error = str(e)

        return result

    async def extract_entities_from_chunks(
        self, chunks: list[str], max_concurrent: int = 3
    ) -> ExtractionResult:
        """
        Extract entities from multiple text chunks in parallel.

        Args:
            chunks: List of text chunks to process
            max_concurrent: Maximum concurrent LLM calls

        Returns:
            Combined ExtractionResult from all chunks
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def extract_with_semaphore(chunk: str) -> ExtractionResult:
            async with semaphore:
                return await self.extract_entities_from_text(chunk)

        # Process chunks in parallel
        results = await asyncio.gather(
            *[extract_with_semaphore(chunk) for chunk in chunks], return_exceptions=True
        )

        # Combine results
        combined = ExtractionResult()
        entity_map: dict[str, ExtractedEntity] = {}  # Deduplicate entities
        relationship_set: set = set()  # Deduplicate relationships

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Extraction failed for chunk: {result}")
                continue

            if result.error:
                logger.warning(f"Extraction error: {result.error}")
                continue

            # Merge entities (sum mentions for duplicates)
            for entity in result.entities:
                if entity.name in entity_map:
                    entity_map[entity.name].mentions += entity.mentions
                    # Keep longer description
                    if len(entity.description) > len(entity_map[entity.name].description):
                        entity_map[entity.name].description = entity.description
                else:
                    entity_map[entity.name] = entity

            # Merge relationships (deduplicate)
            for rel in result.relationships:
                rel_key = (rel.from_entity, rel.to_entity, rel.relationship_type)
                if rel_key not in relationship_set:
                    relationship_set.add(rel_key)
                    combined.relationships.append(rel)

            combined.extraction_time += result.extraction_time

        # Convert entity map to list
        combined.entities = list(entity_map.values())

        return combined

    def extract_entities_simple(
        self, text: str, entity_types: list[str] | None = None
    ) -> ExtractionResult:
        """
        Simple rule-based entity extraction (fallback if LLM unavailable).

        This is much less accurate than LLM extraction but can work without API calls.

        Args:
            text: Text to analyze
            entity_types: Types of entities to extract

        Returns:
            ExtractionResult with basic entities
        """
        result = ExtractionResult()

        if entity_types is None:
            entity_types = ["Technology", "Configuration"]

        # Simple heuristics for technology detection
        tech_patterns = {
            r"\b(Python|JavaScript|TypeScript|Java|Go|Rust|C\+\+|Ruby|PHP)\b": "Technology",
            r"\b(FastAPI|Django|Flask|React|Vue|Angular|Express|Next\.js)\b": "Technology",
            r"\b(Docker|Kubernetes|PostgreSQL|MongoDB|Redis|Neo4j|MySQL)\b": "Technology",
            r"\b(AWS|Azure|GCP|Heroku|Vercel|Netlify)\b": "Technology",
            r"\b([A-Z_]{3,})\b(?=\s*=|\s*:)": "Configuration",  # ALL_CAPS variables
        }

        for pattern, entity_type in tech_patterns.items():
            if entity_type not in entity_types:
                continue

            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_name = match if isinstance(match, str) else match[0]
                if entity_name not in [e.name for e in result.entities]:
                    result.entities.append(
                        ExtractedEntity(
                            name=entity_name,
                            type=entity_type,
                            description=f"Detected {entity_type.lower()}",
                            mentions=text.count(entity_name),
                            confidence=0.6,  # Lower confidence for rule-based
                        )
                    )

        return result
