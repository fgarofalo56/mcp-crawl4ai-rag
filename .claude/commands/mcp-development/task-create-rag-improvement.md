# Create RAG Improvement Task

Create a task for improving RAG strategies, embeddings, or search quality.

## Usage
```
/task-create-rag-improvement <improvement_area> [--priority=P1] [--strategy=contextual|hybrid|agentic|reranking]
```

## Description
Creates a structured task for enhancing RAG capabilities, including research on improvement strategies, implementation plan, and measurement approach.

## Implementation

1. **Analyze current RAG performance** (relevance, speed, cost)
2. **Research improvement strategy**
3. **Plan implementation with A/B testing**
4. **Define success metrics**
5. **Create evaluation dataset**

## Task File Structure

```markdown
# Task: Improve RAG - {improvement_area}

**Status**: todo
**Priority**: {priority}
**Estimated Effort**: L
**Task Type**: feature
**Sprint**: Current
**Created**: {date}
**Labels**: rag, performance, quality-improvement

## Description

Improve RAG system performance for {improvement_area} by implementing {strategy}.

**Current Performance**:
- Relevance Score: {current_score}
- Average Query Time: {current_time}ms
- Cost per Query: ${current_cost}

**Target Performance**:
- Relevance Score: > {target_score}
- Average Query Time: < {target_time}ms
- Cost per Query: < ${target_cost}

## Acceptance Criteria

- [ ] Implementation complete and tested
- [ ] A/B testing shows improvement
- [ ] Performance metrics improved
- [ ] Cost impact acceptable
- [ ] Documentation updated
- [ ] Optional feature flag added

## Research & Context

### Current RAG Pipeline

**Chunking Strategy**:
- Method: {current_chunking_method}
- Chunk Size: {chunk_size}
- Overlap: {overlap}

**Embedding Strategy**:
- Model: {embedding_model}
- Dimensions: {dimensions}
- Contextual Enrichment: {enabled/disabled}

**Search Strategy**:
- Vector Search: {enabled/disabled}
- Hybrid Search: {enabled/disabled}
- Reranking: {enabled/disabled}

**Current Issues**:
1. Issue 1 - Impact on user experience
2. Issue 2 - Performance bottleneck
3. Issue 3 - Accuracy problem

### Proposed Improvement: {strategy}

**What It Does**:
[Explanation of the improvement strategy]

**Expected Benefits**:
- ✅ Benefit 1
- ✅ Benefit 2
- ✅ Benefit 3

**Trade-offs**:
- ⚠️ Trade-off 1 (acceptable because...)
- ⚠️ Trade-off 2 (mitigated by...)

**Research References**:
- [Paper/Article 1](link)
- [Implementation Example](link)
- [Benchmark Results](link)

## Implementation Plan

### Step 1: Create Evaluation Dataset

**Create**: `tests/evaluation/rag_test_queries.json`

```json
{
  "test_queries": [
    {
      "id": 1,
      "query": "How do I crawl a website with Crawl4AI?",
      "expected_docs": ["url1", "url2"],
      "category": "basic_usage"
    },
    {
      "id": 2,
      "query": "How to enable knowledge graph validation?",
      "expected_docs": ["url3", "url4"],
      "category": "advanced_feature"
    }
  ],
  "evaluation_metrics": [
    "precision@5",
    "recall@5",
    "mrr",
    "ndcg"
  ]
}
```

### Step 2: Implement Baseline Measurement

**Create**: `scripts/evaluate_rag.py`

```python
import json
import asyncio
from src.utils import perform_rag_query

async def evaluate_rag_performance():
    \"\"\"Evaluate current RAG performance.\"\"\"
    with open("tests/evaluation/rag_test_queries.json") as f:
        test_data = json.load(f)

    results = []
    for query_data in test_data["test_queries"]:
        query = query_data["query"]
        expected = query_data["expected_docs"]

        # Perform search
        result = await perform_rag_query(query)

        # Calculate metrics
        precision = calculate_precision(result, expected)
        recall = calculate_recall(result, expected)

        results.append({
            "query_id": query_data["id"],
            "precision": precision,
            "recall": recall
        })

    return results

# Baseline results
baseline = asyncio.run(evaluate_rag_performance())
print(f"Baseline Precision: {avg_precision(baseline)}")
print(f"Baseline Recall: {avg_recall(baseline)}")
```

### Step 3: Implement Improvement

**Files to modify**:
- `src/utils.py` - Add new RAG strategy
- `src/config.py` - Add feature flag

**Implementation**:
```python
# src/utils.py

async def perform_rag_query_improved(
    query: str,
    strategy: str = "improved",
    enable_new_feature: bool = True
):
    \"\"\"Improved RAG query with {strategy}.

    Args:
        query: Search query
        strategy: RAG strategy to use
        enable_new_feature: Enable improvement

    Returns:
        Search results with improved relevance
    \"\"\"
    if enable_new_feature:
        # New improved logic
        processed_query = preprocess_query_enhanced(query)
        embeddings = await create_enhanced_embeddings(processed_query)
        results = await search_with_improvements(embeddings)
        return rerank_results_v2(results, query)
    else:
        # Fall back to original
        return await perform_rag_query_original(query)
```

**Feature Flag**:
```python
# .env
USE_IMPROVED_RAG=false  # Default to false for gradual rollout
```

### Step 4: A/B Testing

**Create**: `scripts/ab_test_rag.py`

```python
async def run_ab_test():
    \"\"\"Run A/B test comparing strategies.\"\"\"
    test_queries = load_test_queries()

    # Test baseline
    baseline_results = []
    for query in test_queries:
        result = await perform_rag_query_original(query)
        baseline_results.append(result)

    # Test improved
    improved_results = []
    for query in test_queries:
        result = await perform_rag_query_improved(query)
        improved_results.append(result)

    # Compare
    comparison = compare_results(baseline_results, improved_results)
    print(json.dumps(comparison, indent=2))
```

### Step 5: Measurement & Validation

**Metrics to Track**:
- Precision@5: {target}
- Recall@5: {target}
- MRR (Mean Reciprocal Rank): {target}
- NDCG (Normalized Discounted Cumulative Gain): {target}
- Query Latency: < {target}ms
- Cost per Query: < ${target}

## Testing Requirements

### Evaluation Dataset
- [ ] 50+ test queries covering different categories
- [ ] Ground truth relevance labels
- [ ] Diverse query types (simple, complex, multi-intent)

### Performance Testing
- [ ] Baseline measurements captured
- [ ] Improvement measurements captured
- [ ] Statistical significance verified
- [ ] A/B test results documented

### Load Testing
- [ ] Test under normal load
- [ ] Test under peak load
- [ ] Verify no performance degradation

## Success Metrics

### Primary Metrics
| Metric | Baseline | Target | Must Improve |
|--------|----------|--------|--------------|
| Precision@5 | {baseline} | {target} | Yes |
| Query Time | {baseline}ms | {target}ms | No (acceptable trade-off) |
| Cost/Query | ${baseline} | ${target} | Yes |

### Secondary Metrics
- User satisfaction (if measurable)
- Coverage of documentation
- Edge case handling

## Rollout Plan

### Phase 1: Internal Testing (Week 1)
- [ ] Deploy to test environment
- [ ] Run evaluation suite
- [ ] Collect metrics
- [ ] Analyze results

### Phase 2: Gradual Rollout (Week 2)
- [ ] Enable for 10% of queries
- [ ] Monitor metrics
- [ ] Adjust if needed
- [ ] Increase to 25%

### Phase 3: Full Rollout (Week 3)
- [ ] Enable for 50% of queries
- [ ] Monitor performance
- [ ] Enable for 100% if successful
- [ ] Document learnings

### Rollback Plan
If metrics degrade:
1. Immediately disable feature flag
2. Investigate root cause
3. Fix issues
4. Re-test before re-rollout

## Cost Analysis

### Current Costs
- Embedding calls: {cost_per_1000_queries}
- LLM calls: {cost_per_1000_queries}
- Reranking: {cost_per_1000_queries}
- **Total**: ${total_current_cost}/1000 queries

### Expected Costs After Improvement
- Embedding calls: {new_cost}
- LLM calls: {new_cost}
- Reranking: {new_cost}
- **Total**: ${total_new_cost}/1000 queries

**Cost Change**: {increase/decrease} of {percentage}%

## Documentation Updates

- [ ] Update README.md with new RAG strategy
- [ ] Document configuration options
- [ ] Add usage examples
- [ ] Update performance benchmarks
- [ ] Document cost implications

## Definition of Done

- [ ] Implementation complete
- [ ] A/B testing shows improvement
- [ ] Metrics meet targets
- [ ] Cost impact acceptable
- [ ] Documentation complete
- [ ] Feature flag working
- [ ] Rollout plan approved

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance regression | High | A/B testing, gradual rollout |
| Cost increase | Medium | Monitor costs, set budgets |
| Accuracy decrease | High | Comprehensive evaluation dataset |
| Complexity increase | Low | Good documentation, code review |
```

## Example Usage

```bash
/task-create-rag-improvement contextual-embeddings --priority=P1 --strategy=contextual
```

Creates a task for implementing contextual embeddings to improve RAG relevance.

## Strategies

- `contextual` - Add document context to chunk embeddings
- `hybrid` - Combine vector and keyword search
- `agentic` - Specialized code example extraction
- `reranking` - Cross-encoder reranking
- `chunking` - Improved chunking strategy

## Output

Comprehensive RAG improvement task with evaluation framework, A/B testing plan, and rollout strategy.
