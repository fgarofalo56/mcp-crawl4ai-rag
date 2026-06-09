# Knowledge Base Examples

## Comprehensive Knowledge Base Usage Patterns

This guide demonstrates effective knowledge base management using the Claude Code Context Engineering system, from storing learnings to extracting patterns and evolving your organizational knowledge.

## Table of Contents

1. [Basic Knowledge Storage](#basic-storage)
2. [Knowledge Organization](#organization)
3. [Pattern Extraction](#pattern-extraction)
4. [Knowledge-Driven Development](#driven-dev)
5. [Team Knowledge Sharing](#team-sharing)
6. [Knowledge Evolution](#evolution)
7. [Advanced Queries](#advanced-queries)
8. [Complete Example](#complete-example)

## Basic Storage

### Getting Started with Knowledge Base

#### Step 1: Initial Knowledge Entry

```bash
# Add your first learning
/kb-add "API Design" "Always version your REST APIs from the start using /v1/ prefix"

# System response:
# ✓ Knowledge added to category: API Design
# ✓ Entry ID: kb_001
# ✓ Timestamp: 2024-01-15T10:30:00Z
```

#### Step 2: Structured Knowledge Entry

```bash
# Add detailed learning with context
/kb-add "Database Optimization" \
  "Use connection pooling with min=5, max=20 for PostgreSQL in production. \
   This prevents connection exhaustion while maintaining performance. \
   Tested with 1000 concurrent users."

# Add learning with tags
/kb-add "Security" \
  "Implement rate limiting: 100 req/min for anonymous, 1000 req/min for authenticated" \
  --tags "api,security,performance"

# Add learning with source
/kb-add "React Patterns" \
  "Use React.memo() for expensive components that receive stable props" \
  --source "performance-audit-2024-01.md"
```

#### Step 3: Code Snippet Storage

```bash
# Store code pattern
/kb-add "Error Handling" '
```python
# Consistent error handling pattern
class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        "error": error.message,
        "status": error.status_code
    }
    if error.payload:
        response["details"] = error.payload
    return jsonify(response), error.status_code
```
'
```

## Organization

### Structuring Your Knowledge Base

#### Step 1: Category Management

```bash
# View all categories
/kb-categories

# Output:
# Knowledge Base Categories:
# ├── API Design (15 entries)
# ├── Database Optimization (8 entries)
# ├── Security (12 entries)
# ├── React Patterns (20 entries)
# ├── Testing Strategies (10 entries)
# └── DevOps (7 entries)

# Reorganize categories
/kb-reorganize "API Design" --rename "API Architecture"
/kb-reorganize "React Patterns" --merge-into "Frontend Development"
```

#### Step 2: Hierarchical Organization

```yaml
# knowledge-structure.yaml
categories:
  Architecture:
    subcategories:
      - API Design:
          topics:
            - RESTful principles
            - GraphQL patterns
            - Versioning strategies
      - Microservices:
          topics:
            - Service communication
            - Data consistency
            - Deployment strategies
      - Database:
          topics:
            - Query optimization
            - Schema design
            - Migration strategies

  Frontend:
    subcategories:
      - React:
          topics:
            - Component patterns
            - State management
            - Performance optimization
      - Testing:
          topics:
            - Unit testing
            - Integration testing
            - E2E testing

  DevOps:
    subcategories:
      - CI/CD:
          topics:
            - Pipeline optimization
            - Deployment strategies
            - Rollback procedures
      - Monitoring:
          topics:
            - Metrics collection
            - Alert configuration
            - Log aggregation
```

#### Step 3: Tagging Strategy

```bash
# Define consistent tagging system
/kb-tags-define '
{
  "priority": ["critical", "high", "medium", "low"],
  "type": ["pattern", "antipattern", "bestpractice", "lesson"],
  "phase": ["design", "development", "testing", "deployment"],
  "technology": ["python", "javascript", "docker", "kubernetes", "aws"]
}'

# Apply tags systematically
/kb-retag --category "API Design" --add-tags "type:pattern,phase:design"
/kb-retag --search "security" --add-tags "priority:critical"
```

## Pattern Extraction

### Automated Pattern Discovery

#### Step 1: Extract Patterns from Codebase

```bash
# Scan codebase for patterns
/kb-extract-patterns --source ./src --language python

# System output:
# ✓ Scanning codebase...
# ✓ Analyzing 145 files...
# ✓ Patterns discovered:
#
# 1. Decorator Pattern Usage (15 occurrences)
#    - Authentication decorators: @require_auth
#    - Caching decorators: @cached(ttl=300)
#    - Validation decorators: @validate_schema
#
# 2. Error Handling Pattern (23 occurrences)
#    - Consistent try-except-finally blocks
#    - Custom exception hierarchy
#    - Error logging with context
#
# 3. Database Query Pattern (31 occurrences)
#    - Query builder pattern
#    - Connection pooling
#    - Transaction management
#
# ✓ Added 12 new patterns to knowledge base
```

#### Step 2: Pattern Analysis

```python
# pattern_analyzer.py
from typing import List, Dict
import ast
import os

class PatternAnalyzer:
    """Analyze code patterns and extract learnings"""

    def analyze_project(self, path: str) -> Dict[str, List[str]]:
        patterns = {
            'decorators': [],
            'context_managers': [],
            'error_handling': [],
            'design_patterns': []
        }

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    patterns = self.analyze_file(filepath, patterns)

        return patterns

    def analyze_file(self, filepath: str, patterns: Dict) -> Dict:
        with open(filepath, 'r') as f:
            try:
                tree = ast.parse(f.read())
                self.extract_patterns(tree, patterns)
            except SyntaxError:
                pass
        return patterns

    def extract_patterns(self, tree: ast.AST, patterns: Dict):
        for node in ast.walk(tree):
            # Find decorator patterns
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    patterns['decorators'].append(ast.unparse(decorator))

            # Find context manager patterns
            if isinstance(node, ast.With):
                patterns['context_managers'].append(ast.unparse(node))

            # Find error handling patterns
            if isinstance(node, ast.Try):
                patterns['error_handling'].append(ast.unparse(node))

        return patterns

# Usage
analyzer = PatternAnalyzer()
patterns = analyzer.analyze_project('./src')

# Store patterns in knowledge base
for category, items in patterns.items():
    for pattern in set(items):  # Unique patterns
        command = f'/kb-add "Code Patterns" "{category}: {pattern}"'
        os.system(command)
```

#### Step 3: Pattern Validation

```bash
# Validate patterns against best practices
/kb-validate-patterns

# Output:
# Pattern Validation Report:
# ========================
#
# ✓ Authentication Pattern: VALID
#   Follows OWASP guidelines
#
# ⚠ Caching Pattern: NEEDS REVIEW
#   Missing cache invalidation strategy
#   Recommendation: Add cache versioning
#
# ✓ Error Handling: VALID
#   Comprehensive exception hierarchy
#
# ✗ Database Pattern: ISSUE FOUND
#   SQL injection vulnerability in dynamic queries
#   Fix: Use parameterized queries
#
# Actions:
# - 2 patterns marked for review
# - 1 critical issue requires immediate fix
# - Generated fix suggestions in: kb-fixes.md
```

## Driven Dev

### Knowledge-Driven Development Workflow

#### Step 1: Query Knowledge Before Implementation

```bash
# Before starting new feature
/kb-search "user authentication"

# Results:
# Found 8 relevant entries:
#
# 1. [Security] JWT Token Best Practices
#    - Use RS256 for production, HS256 for development
#    - Token expiry: 15 min access, 7 days refresh
#    - Store refresh tokens in httpOnly cookies
#
# 2. [API Design] Authentication Endpoints
#    - POST /auth/login - Returns access and refresh tokens
#    - POST /auth/refresh - Refreshes access token
#    - POST /auth/logout - Invalidates refresh token
#
# 3. [Code Pattern] Authentication Middleware
#    ```python
#    async def authenticate(request):
#        token = request.headers.get('Authorization')
#        if not token:
#            raise Unauthorized()
#        user = verify_jwt(token)
#        request.state.user = user
#    ```
```

#### Step 2: Apply Knowledge in Development

```python
# auth_service.py - Implementing based on KB patterns
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

# Applied from KB: JWT configuration
JWT_CONFIG = {
    'algorithm': 'RS256',  # KB recommendation
    'access_expiry': timedelta(minutes=15),  # KB recommendation
    'refresh_expiry': timedelta(days=7)  # KB recommendation
}

class AuthService:
    """Authentication service following KB patterns"""

    def __init__(self):
        # KB Pattern: Load keys securely
        self.private_key = self.load_private_key()
        self.public_key = self.load_public_key()

    def create_tokens(self, user_id: str) -> dict:
        """Create access and refresh tokens - KB Pattern"""
        now = datetime.utcnow()

        # Access token
        access_payload = {
            'sub': user_id,
            'type': 'access',
            'iat': now,
            'exp': now + JWT_CONFIG['access_expiry']
        }
        access_token = jwt.encode(
            access_payload,
            self.private_key,
            algorithm=JWT_CONFIG['algorithm']
        )

        # Refresh token
        refresh_payload = {
            'sub': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + JWT_CONFIG['refresh_expiry']
        }
        refresh_token = jwt.encode(
            refresh_payload,
            self.private_key,
            algorithm=JWT_CONFIG['algorithm']
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }

    def verify_token(self, token: str, token_type: str = 'access') -> dict:
        """Verify JWT token - KB Pattern"""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[JWT_CONFIG['algorithm']]
            )

            # KB Pattern: Validate token type
            if payload.get('type') != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# KB Pattern: Authentication dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token - KB Pattern"""
    auth_service = AuthService()
    payload = auth_service.verify_token(credentials.credentials)
    user_id = payload.get('sub')

    # KB Pattern: Cache user lookup
    user = await get_user_from_cache_or_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

#### Step 3: Document New Learnings

```bash
# After implementation, add new learnings
/kb-add "Authentication" \
  "RS256 requires ~10ms more per request than HS256 but provides better security. \
   Acceptable tradeoff for production systems." \
  --tags "performance,security,measured"

/kb-add "Caching" \
  "Cache user objects for 5 minutes after authentication to reduce DB queries. \
   Invalidate on user update events." \
  --source "auth_service.py"
```

## Team Sharing

### Collaborative Knowledge Management

#### Step 1: Export Knowledge for Team

```bash
# Export knowledge base
/kb-export --format markdown --output team-knowledge.md

# Export specific categories
/kb-export --categories "API Design,Security" --format json --output api-knowledge.json

# Generate knowledge report
/kb-report --period "last-month" --output monthly-learnings.html
```

#### Generated Report Example

```markdown
# Team Knowledge Report - January 2024

## Summary
- **Total Entries**: 127
- **New This Month**: 23
- **Most Active Categories**: API Design (8), Security (6), Performance (5)
- **Top Contributors**: alice (12), bob (7), charlie (4)

## Key Learnings This Month

### 1. API Rate Limiting Strategy
**Category**: API Design | **Date**: 2024-01-10 | **Impact**: High

Implemented sliding window rate limiting with Redis:
- 100 requests/minute for anonymous users
- 1000 requests/minute for authenticated users
- 5000 requests/minute for premium users

**Implementation**:
```python
async def check_rate_limit(user_id: str, tier: str) -> bool:
    key = f"rate_limit:{user_id}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)

    limits = {'anonymous': 100, 'standard': 1000, 'premium': 5000}
    return current <= limits.get(tier, 100)
```

**Results**:
- Reduced server load by 40%
- Zero legitimate users blocked
- Prevented 12,000 bot requests/day

### 2. Database Query Optimization
**Category**: Performance | **Date**: 2024-01-15 | **Impact**: Critical

Discovered N+1 query issue in order processing:

**Before**:
```python
orders = Order.query.all()
for order in orders:
    user = User.query.get(order.user_id)  # N+1 problem
```

**After**:
```python
orders = Order.query.options(joinedload(Order.user)).all()
```

**Results**:
- Page load time: 3.2s → 0.4s
- Database queries: 1001 → 1
- CPU usage: -65%

## Pattern Evolution

### Authentication Patterns
- **Week 1**: Basic JWT implementation
- **Week 2**: Added refresh token rotation
- **Week 3**: Implemented token blacklisting
- **Week 4**: Added device fingerprinting

## Recommendations

1. **Standardize Error Handling**: Multiple patterns found, need consolidation
2. **Document Rate Limiting**: Add to API documentation
3. **Security Audit**: Schedule for February based on new patterns

## Action Items
- [ ] Update API documentation with rate limits
- [ ] Refactor error handling to use standard pattern
- [ ] Create performance testing suite
- [ ] Schedule knowledge sharing session
```

#### Step 2: Knowledge Sharing Sessions

```python
# knowledge_sharing.py
from datetime import datetime
import json

class KnowledgeSharing:
    """Facilitate team knowledge sharing"""

    def prepare_session(self, topic: str):
        """Prepare knowledge sharing session materials"""

        # Query relevant knowledge
        knowledge = self.query_knowledge(topic)

        # Generate presentation outline
        outline = {
            'title': f"Knowledge Sharing: {topic}",
            'date': datetime.now().isoformat(),
            'agenda': [
                'Overview of collected knowledge',
                'Key patterns and best practices',
                'Common pitfalls to avoid',
                'Hands-on examples',
                'Q&A and discussion'
            ],
            'content': knowledge,
            'exercises': self.generate_exercises(knowledge)
        }

        return outline

    def generate_exercises(self, knowledge):
        """Generate practical exercises from knowledge"""
        exercises = []

        for item in knowledge:
            if 'code' in item:
                exercises.append({
                    'type': 'implementation',
                    'task': f"Implement the {item['pattern']} pattern",
                    'starter_code': item['code'],
                    'validation': item.get('tests', [])
                })

        return exercises

    def track_adoption(self, pattern_id: str):
        """Track pattern adoption across team"""
        adoption = {
            'pattern_id': pattern_id,
            'adopters': [],
            'implementations': [],
            'feedback': []
        }

        # Monitor codebase for pattern usage
        # Track who implements it
        # Collect feedback

        return adoption
```

## Evolution

### Knowledge Base Evolution Over Time

#### Step 1: Track Knowledge Growth

```python
# kb_analytics.py
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

class KnowledgeAnalytics:
    """Analyze knowledge base evolution"""

    def analyze_growth(self, kb_data):
        """Analyze knowledge base growth patterns"""

        # Create timeline
        df = pd.DataFrame(kb_data)
        df['date'] = pd.to_datetime(df['created_at'])
        df.set_index('date', inplace=True)

        # Growth metrics
        metrics = {
            'total_entries': len(df),
            'entries_per_month': df.resample('M').size().mean(),
            'top_categories': df['category'].value_counts().head(5),
            'avg_entry_length': df['content'].str.len().mean(),
            'pattern_reuse': self.calculate_reuse_rate(df)
        }

        return metrics

    def calculate_reuse_rate(self, df):
        """Calculate how often patterns are reused"""
        reuse_count = 0
        for entry in df.itertuples():
            if 'applied' in entry.tags or 'reused' in entry.tags:
                reuse_count += 1

        return (reuse_count / len(df)) * 100

    def identify_outdated(self, kb_data, threshold_days=180):
        """Identify potentially outdated knowledge"""
        outdated = []
        cutoff = datetime.now() - timedelta(days=threshold_days)

        for entry in kb_data:
            last_accessed = entry.get('last_accessed', entry['created_at'])
            if last_accessed < cutoff:
                outdated.append({
                    'id': entry['id'],
                    'title': entry['title'],
                    'age_days': (datetime.now() - last_accessed).days,
                    'category': entry['category']
                })

        return outdated

    def generate_insights(self, kb_data):
        """Generate actionable insights from KB"""
        insights = []

        # Pattern frequency analysis
        pattern_freq = self.analyze_pattern_frequency(kb_data)
        if pattern_freq['most_common']:
            insights.append(
                f"Most used pattern: {pattern_freq['most_common']} "
                f"({pattern_freq['usage_count']} times)"
            )

        # Knowledge gaps
        gaps = self.identify_knowledge_gaps(kb_data)
        if gaps:
            insights.append(f"Knowledge gaps identified in: {', '.join(gaps)}")

        # Success patterns
        success = self.identify_success_patterns(kb_data)
        insights.extend(success)

        return insights
```

#### Step 2: Knowledge Refinement Process

```bash
# Regular knowledge review and refinement
/kb-review --age ">6months"

# Output:
# Knowledge Review Report
# ======================
#
# Entries for Review (12):
#
# 1. [API Design] REST vs GraphQL comparison
#    Age: 8 months | Last accessed: 6 months ago
#    Status: Potentially outdated
#    Action: Review against current GraphQL Federation patterns
#
# 2. [Security] Password hashing with bcrypt
#    Age: 10 months | Last accessed: 2 weeks ago
#    Status: Still relevant but needs update
#    Action: Add Argon2 as recommended alternative
#
# Automated Actions:
# - Archived 3 obsolete entries
# - Merged 2 duplicate patterns
# - Updated 5 entries with new information
# - Tagged 4 entries for expert review
```

#### Step 3: Knowledge Versioning

```yaml
# kb-version-history.yaml
entry_id: kb_security_001
title: "Authentication Best Practices"
versions:
  - version: 1.0
    date: 2023-06-01
    content: "Use JWT with HS256 for stateless auth"
    tags: ["security", "jwt"]

  - version: 2.0
    date: 2023-09-15
    content: "Use JWT with RS256 for better security"
    changes: "Updated algorithm recommendation"
    tags: ["security", "jwt", "updated"]

  - version: 3.0
    date: 2024-01-10
    content: |
      Use JWT with RS256 for production
      Implement refresh token rotation
      Add rate limiting per user
    changes: "Added refresh token and rate limiting patterns"
    tags: ["security", "jwt", "comprehensive"]

migration_notes:
  from_v1_to_v2: "Update JWT library and regenerate keys"
  from_v2_to_v3: "Implement refresh token endpoint and Redis for rate limiting"
```

## Advanced Queries

### Complex Knowledge Base Queries

#### Step 1: Multi-Criteria Search

```bash
# Complex search with multiple criteria
/kb-search \
  --category "API Design" \
  --tags "security,performance" \
  --date-range "2024-01-01:2024-01-31" \
  --author "team:backend" \
  --impact "high"

# Semantic search
/kb-search-semantic "How to handle database connection pooling in microservices"

# Pattern-based search
/kb-search-pattern "decorator @.* def .*\(.*\):"
```

#### Step 2: Knowledge Relationships

```python
# kb_graph.py
import networkx as nx
from typing import List, Dict

class KnowledgeGraph:
    """Build and query knowledge relationship graph"""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, kb_entries: List[Dict]):
        """Build relationship graph from KB entries"""

        for entry in kb_entries:
            # Add node
            self.graph.add_node(
                entry['id'],
                title=entry['title'],
                category=entry['category'],
                content=entry['content']
            )

            # Add edges based on references
            for ref in entry.get('references', []):
                self.graph.add_edge(entry['id'], ref, type='references')

            # Add edges based on tags
            for tag in entry.get('tags', []):
                tag_node = f"tag:{tag}"
                self.graph.add_node(tag_node, type='tag')
                self.graph.add_edge(entry['id'], tag_node, type='tagged')

    def find_related(self, entry_id: str, depth: int = 2) -> List[str]:
        """Find related knowledge entries"""
        related = []

        # Use BFS to find related nodes
        for node in nx.bfs_tree(self.graph, entry_id, depth_limit=depth):
            if node != entry_id and not node.startswith('tag:'):
                related.append(node)

        return related

    def find_patterns(self) -> Dict[str, List]:
        """Identify common patterns in knowledge graph"""
        patterns = {
            'hubs': [],  # Highly referenced entries
            'clusters': [],  # Groups of related entries
            'bridges': []  # Entries connecting different domains
        }

        # Find hubs (high in-degree)
        for node in self.graph.nodes():
            if self.graph.in_degree(node) > 5:
                patterns['hubs'].append(node)

        # Find clusters
        clusters = nx.community.louvain_communities(self.graph.to_undirected())
        patterns['clusters'] = [list(cluster) for cluster in clusters]

        # Find bridges
        for node in self.graph.nodes():
            if nx.node_connectivity(self.graph.to_undirected(), node) > 3:
                patterns['bridges'].append(node)

        return patterns
```

#### Step 3: AI-Powered Analysis

```bash
# Use AI to analyze and synthesize knowledge
/kb-ai-analyze "What are our most successful patterns for handling errors?"

# AI Analysis Result:
# ==================
#
# Based on 47 knowledge entries about error handling:
#
# **Most Successful Patterns:**
#
# 1. **Centralized Error Handler** (Used in 12 projects, 100% success rate)
#    - Single error handling middleware
#    - Consistent error response format
#    - Automatic logging and monitoring
#
# 2. **Error Recovery Strategy** (Used in 8 projects, 87% success rate)
#    - Exponential backoff for retries
#    - Circuit breaker for external services
#    - Graceful degradation
#
# 3. **Structured Error Types** (Used in 15 projects, 93% success rate)
#    ```python
#    class AppError(Exception):
#        def __init__(self, message, code, details=None):
#            self.message = message
#            self.code = code
#            self.details = details
#    ```
#
# **Key Success Factors:**
# - Consistency across services (mentioned 23 times)
# - Proper error context (mentioned 19 times)
# - User-friendly messages (mentioned 15 times)
#
# **Recommendations:**
# 1. Standardize on pattern #1 for all new services
# 2. Document error codes in central registry
# 3. Add error tracking dashboard
```

## Complete Example

### End-to-End Knowledge Base Workflow

#### Step 1: Project Initialization with KB

```bash
# Start new project with knowledge base consultation
/project-init "Payment Processing Service"

# System queries knowledge base:
# ✓ Found 23 relevant entries for "payment processing"
# ✓ Found 15 security considerations
# ✓ Found 8 compliance requirements
# ✓ Found 12 integration patterns

# Applying knowledge to project setup...
```

#### Step 2: Generated Project Structure with KB Insights

```python
# payment_service.py - Generated with KB patterns
"""
Payment Processing Service
Generated with knowledge from 23 KB entries
"""

import stripe
from decimal import Decimal
from typing import Optional
import logging

# KB Pattern: Comprehensive logging
logger = logging.getLogger(__name__)

# KB Pattern: Configuration from environment
class PaymentConfig:
    """Payment configuration following PCI compliance - KB Entry #sec_042"""

    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # KB Pattern: Idempotency for payment operations
    IDEMPOTENCY_TIMEOUT = 3600  # 1 hour

    # KB Pattern: Rate limiting for payment APIs
    RATE_LIMIT = {
        'create_payment': 10,  # per minute
        'refund': 5,  # per minute
        'webhook': 100  # per minute
    }

class PaymentService:
    """Payment service with KB best practices applied"""

    def __init__(self):
        # KB Pattern: Initialize with proper error handling
        try:
            stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY
            self.redis = self.init_redis()  # For idempotency
        except Exception as e:
            logger.error(f"Payment service initialization failed: {e}")
            raise

    async def process_payment(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        idempotency_key: Optional[str] = None
    ):
        """
        Process payment with KB patterns:
        - Idempotency (KB #api_015)
        - Decimal for money (KB #finance_003)
        - Comprehensive logging (KB #debug_007)
        - Retry logic (KB #reliability_011)
        """

        # KB Pattern: Idempotency check
        if idempotency_key:
            cached = await self.redis.get(f"payment:{idempotency_key}")
            if cached:
                logger.info(f"Returning cached payment for key: {idempotency_key}")
                return json.loads(cached)

        # KB Pattern: Input validation
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # KB Pattern: Convert decimal to cents
        amount_cents = int(amount * 100)

        # KB Pattern: Retry logic with exponential backoff
        for attempt in range(3):
            try:
                # Create payment intent
                intent = stripe.PaymentIntent.create(
                    amount=amount_cents,
                    currency=currency,
                    customer=customer_id,
                    idempotency_key=idempotency_key,
                    metadata={
                        'service': 'payment_processing',
                        'version': '1.0.0'
                    }
                )

                # KB Pattern: Store for idempotency
                if idempotency_key:
                    await self.redis.setex(
                        f"payment:{idempotency_key}",
                        PaymentConfig.IDEMPOTENCY_TIMEOUT,
                        json.dumps(intent)
                    )

                # KB Pattern: Audit logging
                logger.info(f"Payment processed: {intent.id} for customer: {customer_id}")

                return intent

            except stripe.error.RateLimitError:
                # KB Pattern: Handle rate limiting
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, waiting {wait_time}s")
                await asyncio.sleep(wait_time)

            except stripe.error.StripeError as e:
                # KB Pattern: Structured error handling
                logger.error(f"Stripe error: {e.user_message}")
                raise PaymentError(
                    message=e.user_message,
                    code=e.code,
                    details={'stripe_error': str(e)}
                )

        raise PaymentError("Payment failed after retries")

    async def handle_webhook(self, payload: str, signature: str):
        """
        Handle Stripe webhooks with KB patterns:
        - Signature verification (KB #security_028)
        - Event deduplication (KB #webhook_005)
        - Async processing (KB #performance_019)
        """

        # KB Pattern: Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, PaymentConfig.WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid webhook payload")
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise ValueError("Invalid signature")

        # KB Pattern: Prevent duplicate processing
        event_key = f"webhook:{event['id']}"
        if await self.redis.exists(event_key):
            logger.info(f"Duplicate webhook ignored: {event['id']}")
            return {"status": "duplicate"}

        # Mark as processed
        await self.redis.setex(event_key, 86400, "processed")  # 24 hours

        # KB Pattern: Async event processing
        await self.process_webhook_event(event)

        return {"status": "processed"}

# KB Pattern: Custom exception hierarchy
class PaymentError(Exception):
    """Payment processing error - KB #error_009"""
    def __init__(self, message: str, code: str = "payment_error", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
```

#### Step 3: Testing with KB Patterns

```python
# test_payment_service.py - Tests based on KB patterns
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

class TestPaymentService:
    """Test suite following KB testing patterns"""

    @pytest.fixture
    def payment_service(self):
        """KB Pattern: Test fixture with mocked dependencies"""
        with patch('stripe.api_key'):
            service = PaymentService()
            service.redis = Mock()  # Mock Redis
            return service

    @pytest.mark.asyncio
    async def test_idempotency(self, payment_service):
        """KB Pattern: Test idempotency - KB #testing_024"""
        # Setup
        idempotency_key = "test_key_123"
        payment_service.redis.get.return_value = None

        # First call
        with patch('stripe.PaymentIntent.create') as mock_create:
            mock_create.return_value = {'id': 'pi_123', 'status': 'succeeded'}

            result1 = await payment_service.process_payment(
                amount=Decimal('99.99'),
                currency='usd',
                customer_id='cust_123',
                idempotency_key=idempotency_key
            )

        # Second call with same key (should return cached)
        payment_service.redis.get.return_value = json.dumps(result1)

        result2 = await payment_service.process_payment(
            amount=Decimal('99.99'),
            currency='usd',
            customer_id='cust_123',
            idempotency_key=idempotency_key
        )

        # Verify stripe was only called once
        assert mock_create.call_count == 1
        assert result1 == json.loads(result2)

    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self, payment_service):
        """KB Pattern: Security testing - KB #security_test_015"""
        # Invalid signature should raise
        with pytest.raises(ValueError, match="Invalid signature"):
            await payment_service.handle_webhook(
                payload="fake_payload",
                signature="invalid_signature"
            )

    @pytest.mark.parametrize("amount,should_fail", [
        (Decimal('0'), True),      # KB: Zero amount invalid
        (Decimal('-10'), True),     # KB: Negative amount invalid
        (Decimal('0.01'), False),   # KB: Minimum valid amount
        (Decimal('999999'), False), # KB: Large amount valid
    ])
    @pytest.mark.asyncio
    async def test_amount_validation(self, payment_service, amount, should_fail):
        """KB Pattern: Parametrized validation testing - KB #testing_031"""
        if should_fail:
            with pytest.raises(ValueError):
                await payment_service.process_payment(
                    amount=amount,
                    currency='usd',
                    customer_id='cust_123'
                )
        else:
            with patch('stripe.PaymentIntent.create'):
                # Should not raise
                await payment_service.process_payment(
                    amount=amount,
                    currency='usd',
                    customer_id='cust_123'
                )
```

#### Step 4: Documentation with KB References

```markdown
# Payment Processing Service

## Overview

This payment processing service implements industry best practices collected from our knowledge base over 2 years of payment system development.

## Key Patterns Applied

### 1. Idempotency (KB #api_015)
All payment operations are idempotent using Redis-based caching with 1-hour TTL.

### 2. Money Handling (KB #finance_003)
- Use `Decimal` type for all monetary values
- Store amounts in cents to avoid floating-point errors
- Always specify currency explicitly

### 3. Security (KB #security_028, #security_042)
- Webhook signature verification
- PCI compliance through Stripe
- No card data stored locally
- Comprehensive audit logging

### 4. Error Handling (KB #error_009, #reliability_011)
- Structured error types with codes
- Exponential backoff for retries
- Rate limiting handling
- User-friendly error messages

## Configuration

Based on KB #config_008, all configuration uses environment variables:

```bash
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLIC_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export REDIS_URL="redis://localhost:6379"
```

## Testing

Following KB #testing_024 and #testing_031:

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=payment_service --cov-report=html
```

## Monitoring

Implements KB #monitoring_014 patterns:

- Structured logging with correlation IDs
- Metrics exported to Prometheus
- Custom alerts for payment failures
- Dashboard in Grafana

## Lessons Learned

This implementation incorporates learnings from:
- 12 payment integration projects
- 47 documented error scenarios
- 23 security audits
- 8 compliance reviews

See knowledge base for detailed patterns and their evolution.
```

#### Step 5: Continuous Knowledge Updates

```bash
# After deployment, update knowledge base
/kb-add "Payment Processing" \
  "Stripe webhook events can arrive out of order. Always check payment intent status \
   rather than relying on event sequence. Discovered in production after processing \
   10,000 payments." \
  --tags "stripe,webhooks,production-learning" \
  --impact "high"

# Link to implementation
/kb-link kb_payment_001 --code "payment_service.py:L145-L162"

# Track success metrics
/kb-metric kb_payment_001 \
  --metric "error-rate" \
  --value "0.01%" \
  --context "After 30 days in production"
```

## Summary

This comprehensive knowledge base guide demonstrates:

1. **Storage**: Systematic knowledge capture
2. **Organization**: Hierarchical categorization
3. **Pattern Extraction**: Automated pattern discovery
4. **Development Integration**: Knowledge-driven coding
5. **Team Collaboration**: Sharing and evolution
6. **Advanced Queries**: Complex knowledge retrieval
7. **Continuous Learning**: Knowledge refinement

The knowledge base becomes a living documentation system that:
- Captures team learnings
- Prevents repeated mistakes
- Accelerates development
- Ensures consistency
- Facilitates onboarding
- Drives continuous improvement

Use these patterns to build and maintain an effective knowledge base with the Claude Code Context Engineering system.
