# 💡 Agent Examples

> **Real-world agent usage examples and multi-agent workflow patterns**

This guide provides practical, real-world examples of using Claude Code agents, from simple single-agent tasks to complex multi-agent coordination patterns.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Single Agent Examples](#-single-agent-examples)
- [Code Review Workflows](#-code-review-workflows)
- [Documentation Generation Workflows](#-documentation-generation-workflows)
- [Multi-Agent Coordination Patterns](#-multi-agent-coordination-patterns)
- [Testing Automation](#-testing-automation)
- [Custom Agent Use Cases](#-custom-agent-use-cases)
- [Complete Working Examples](#-complete-working-examples)
- [Troubleshooting Examples](#-troubleshooting-examples)
- [Related Documentation](#-related-documentation)

---

## 🎯 Overview

This guide contains:
- **10+ single agent examples** with inputs and outputs
- **5+ code review workflows** from simple to comprehensive
- **4+ documentation workflows** for different scenarios
- **8+ multi-agent patterns** showing coordination
- **5+ testing workflows** with automation
- **6+ custom use cases** solving specific problems
- **4+ complete examples** with full code

Each example includes:
- Context and use case
- Agent invocation
- Expected input/output
- Variations and alternatives
- Best practices

---

## 🔧 Single Agent Examples

### Example 1: Python Code Refactoring

**Scenario**: Legacy Python code needs modernization with type hints and better structure

**Agent**: `python-pro`

**Input**:
```python
# legacy_calculator.py
def calc(x, y, op):
    if op == 'add':
        return x + y
    elif op == 'sub':
        return x - y
    elif op == 'mul':
        return x * y
    elif op == 'div':
        if y == 0:
            return None
        return x / y

def process_numbers(nums):
    result = []
    for n in nums:
        if n > 0:
            result.append(n * 2)
    return result
```

**Invocation**:
```
"Use python-pro agent to refactor legacy_calculator.py with type hints, better error handling, and modern Python patterns"
```

**Output**:
```python
# calculator.py
from enum import Enum
from typing import List, Union

class Operation(Enum):
    """Supported mathematical operations."""
    ADD = "add"
    SUBTRACT = "sub"
    MULTIPLY = "mul"
    DIVIDE = "div"

class CalculationError(Exception):
    """Raised when calculation fails."""
    pass

def calculate(
    x: Union[int, float],
    y: Union[int, float],
    operation: Operation
) -> float:
    """Perform mathematical operation on two numbers.

    Args:
        x: First operand
        y: Second operand
        operation: Operation to perform

    Returns:
        Result of the operation

    Raises:
        CalculationError: If operation fails (e.g., division by zero)
        ValueError: If operation is not supported

    Examples:
        >>> calculate(10, 5, Operation.ADD)
        15.0
        >>> calculate(10, 5, Operation.DIVIDE)
        2.0
    """
    operations = {
        Operation.ADD: lambda: x + y,
        Operation.SUBTRACT: lambda: x - y,
        Operation.MULTIPLY: lambda: x * y,
        Operation.DIVIDE: lambda: _safe_divide(x, y),
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    return operations[operation]()

def _safe_divide(x: float, y: float) -> float:
    """Safely divide two numbers.

    Args:
        x: Numerator
        y: Denominator

    Returns:
        Result of division

    Raises:
        CalculationError: If denominator is zero
    """
    if y == 0:
        raise CalculationError("Division by zero")
    return x / y

def process_positive_numbers(numbers: List[float]) -> List[float]:
    """Double all positive numbers in the list.

    Args:
        numbers: List of numbers to process

    Returns:
        List of doubled positive numbers

    Examples:
        >>> process_positive_numbers([1, -2, 3, 0, 4])
        [2.0, 6.0, 8.0]
    """
    return [n * 2 for n in numbers if n > 0]


# tests/test_calculator.py
import pytest
from calculator import calculate, Operation, CalculationError, process_positive_numbers

class TestCalculate:
    """Tests for calculate function."""

    def test_addition(self):
        assert calculate(5, 3, Operation.ADD) == 8.0

    def test_subtraction(self):
        assert calculate(10, 4, Operation.SUBTRACT) == 6.0

    def test_multiplication(self):
        assert calculate(6, 7, Operation.MULTIPLY) == 42.0

    def test_division(self):
        assert calculate(10, 2, Operation.DIVIDE) == 5.0

    def test_division_by_zero_raises_error(self):
        with pytest.raises(CalculationError, match="Division by zero"):
            calculate(10, 0, Operation.DIVIDE)

class TestProcessPositiveNumbers:
    """Tests for process_positive_numbers."""

    def test_filters_and_doubles(self):
        result = process_positive_numbers([1, -2, 3, 0, 4])
        assert result == [2.0, 6.0, 8.0]

    def test_empty_list(self):
        assert process_positive_numbers([]) == []

    def test_all_negative(self):
        assert process_positive_numbers([-1, -2, -3]) == []
```

**Key Improvements**:
- Type hints throughout
- Enum for operations (type-safe)
- Custom exceptions
- Comprehensive docstrings
- Generator expressions
- Complete test coverage

---

### Example 2: API Documentation Generation

**Scenario**: REST API needs OpenAPI specification

**Agent**: `api-documenter`

**Input**:
```python
# api/users.py
@app.get("/users")
def list_users(skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

@app.post("/users")
def create_user(email: str, name: str):
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    return user

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    return user
```

**Invocation**:
```
"Use api-documenter agent to create OpenAPI specification for the users API"
```

**Output**:
```yaml
openapi: 3.0.0
info:
  title: User Management API
  description: API for managing user accounts
  version: 1.0.0
  contact:
    name: API Support
    email: api@example.com

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging.api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List users
      description: Retrieve a paginated list of users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: skip
          in: query
          description: Number of users to skip (for pagination)
          required: false
          schema:
            type: integer
            default: 0
            minimum: 0
        - name: limit
          in: query
          description: Maximum number of users to return
          required: false
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
              examples:
                success:
                  value:
                    - id: 1
                      email: "john@example.com"
                      name: "John Doe"
                      created_at: "2025-01-15T10:30:00Z"
                    - id: 2
                      email: "jane@example.com"
                      name: "Jane Smith"
                      created_at: "2025-01-15T11:00:00Z"

    post:
      summary: Create user
      description: Create a new user account
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  format: email
                  description: User's email address
                name:
                  type: string
                  minLength: 1
                  maxLength: 100
                  description: User's full name
            examples:
              newUser:
                value:
                  email: "new.user@example.com"
                  name: "New User"
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: User already exists

  /users/{user_id}:
    get:
      summary: Get user
      description: Retrieve a specific user by ID
      operationId: getUser
      tags:
        - Users
      parameters:
        - name: user_id
          in: path
          required: true
          description: User ID
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          description: Unique user identifier
          example: 1
        email:
          type: string
          format: email
          description: User's email address
          example: "user@example.com"
        name:
          type: string
          description: User's full name
          example: "John Doe"
        created_at:
          type: string
          format: date-time
          description: Account creation timestamp
          example: "2025-01-15T10:30:00Z"

    Error:
      type: object
      properties:
        error:
          type: string
          description: Error message
        code:
          type: string
          description: Error code
```

**Bonus - curl Examples**:
```bash
# List users
curl -X GET "https://api.example.com/v1/users?skip=0&limit=10"

# Create user
curl -X POST "https://api.example.com/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "new@example.com", "name": "New User"}'

# Get specific user
curl -X GET "https://api.example.com/v1/users/1"
```

---

### Example 3: Testing and Validation

**Scenario**: New feature implemented, needs comprehensive testing

**Agent**: `validation-gates`

**Context**:
```python
# auth.py - New authentication feature
def login(username: str, password: str) -> str:
    """Authenticate user and return JWT token."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise AuthenticationError("Invalid credentials")
    return generate_jwt_token(user)
```

**Invocation**:
```
"Use validation-gates agent to validate the new authentication feature in auth.py. Test login success, failure cases, token generation, and ensure all tests pass."
```

**Agent Actions**:
```bash
# 1. Run linting
$ ruff check auth.py
✅ No linting errors

# 2. Type checking
$ mypy auth.py
✅ Type checking passed

# 3. Run existing tests
$ pytest tests/test_auth.py -v
FAILED tests/test_auth.py::test_login_invalid_username - AssertionError

# 4. Analyze failure
# Agent reads test file, identifies issue in test

# 5. Fix test
# Agent updates test to match actual behavior

# 6. Create missing tests
# Agent generates additional test cases
```

**Generated Tests**:
```python
# tests/test_auth.py
import pytest
from auth import login, AuthenticationError
from models import User

class TestLogin:
    """Tests for login function."""

    def test_login_success_returns_token(self, db_session, user_fixture):
        """Test successful login returns JWT token."""
        token = login(user_fixture.username, "correct_password")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long

    def test_login_invalid_username_raises_error(self, db_session):
        """Test login with non-existent username raises error."""
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            login("nonexistent", "password")

    def test_login_invalid_password_raises_error(self, db_session, user_fixture):
        """Test login with wrong password raises error."""
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            login(user_fixture.username, "wrong_password")

    def test_login_empty_username_raises_error(self, db_session):
        """Test login with empty username raises error."""
        with pytest.raises(AuthenticationError):
            login("", "password")

    def test_login_empty_password_raises_error(self, db_session, user_fixture):
        """Test login with empty password raises error."""
        with pytest.raises(AuthenticationError):
            login(user_fixture.username, "")

    def test_login_token_contains_user_id(self, db_session, user_fixture):
        """Test generated token contains user ID."""
        token = login(user_fixture.username, "correct_password")

        decoded = decode_jwt_token(token)
        assert decoded["user_id"] == user_fixture.id

    def test_login_token_expiration_set(self, db_session, user_fixture):
        """Test generated token has expiration."""
        token = login(user_fixture.username, "correct_password")

        decoded = decode_jwt_token(token)
        assert "exp" in decoded
        assert decoded["exp"] > time.time()

# Fixtures
@pytest.fixture
def user_fixture(db_session):
    """Create test user."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("correct_password")
    db_session.add(user)
    db_session.commit()
    return user
```

**Final Validation**:
```bash
$ pytest tests/test_auth.py -v --cov=auth
======================== test session starts ========================
tests/test_auth.py::test_login_success_returns_token PASSED
tests/test_auth.py::test_login_invalid_username_raises_error PASSED
tests/test_auth.py::test_login_invalid_password_raises_error PASSED
tests/test_auth.py::test_login_empty_username_raises_error PASSED
tests/test_auth.py::test_login_empty_password_raises_error PASSED
tests/test_auth.py::test_login_token_contains_user_id PASSED
tests/test_auth.py::test_login_token_expiration_set PASSED

---------- coverage: platform linux, python 3.11 -----------
Name        Stmts   Miss  Cover
-------------------------------
auth.py        45      2    96%
-------------------------------

======================== 7 passed in 1.24s ==========================

✅ All validation gates passed!
✅ Test coverage: 96%
✅ All tests passing
```

---

### Example 4: Technical Diagram Creation

**Scenario**: Need sequence diagram for authentication flow

**Agent**: `mermaid-expert`

**Invocation**:
```
"Use mermaid-expert agent to create a sequence diagram showing the OAuth2 authentication flow including user, frontend, auth server, and resource server"
```

**Output**:
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FE as Frontend
    participant Auth as Auth Server
    participant Resource as Resource Server
    participant DB as Database

    Note over User,DB: OAuth2 Authorization Code Flow

    User->>FE: Click "Login"
    activate FE

    FE->>Auth: GET /authorize?client_id=...&redirect_uri=...
    activate Auth

    Auth->>User: Show login form
    deactivate Auth

    User->>Auth: POST /login (credentials)
    activate Auth

    Auth->>DB: Verify credentials
    activate DB
    DB-->>Auth: User validated
    deactivate DB

    Auth->>Auth: Generate authorization code
    Auth->>FE: Redirect with auth code
    deactivate Auth

    FE->>Auth: POST /token (auth code)
    activate Auth

    Auth->>DB: Validate auth code
    activate DB
    DB-->>Auth: Code valid
    deactivate DB

    Auth->>Auth: Generate access & refresh tokens
    Auth-->>FE: Return tokens
    deactivate Auth

    FE->>FE: Store tokens securely
    FE-->>User: Redirect to dashboard
    deactivate FE

    Note over User,Resource: Accessing Protected Resource

    User->>FE: Request protected data
    activate FE

    FE->>Resource: GET /api/data<br/>Authorization: Bearer {token}
    activate Resource

    Resource->>Auth: Validate token
    activate Auth
    Auth->>DB: Check token validity
    activate DB
    DB-->>Auth: Token valid
    deactivate DB
    Auth-->>Resource: Token verified
    deactivate Auth

    Resource->>DB: Fetch data
    activate DB
    DB-->>Resource: Data retrieved
    deactivate DB

    Resource-->>FE: Return data
    deactivate Resource

    FE-->>User: Display data
    deactivate FE

    Note over User,DB: Token Refresh (when expired)

    FE->>Auth: POST /token/refresh<br/>(refresh token)
    activate Auth
    Auth->>DB: Validate refresh token
    activate DB
    DB-->>Auth: Refresh token valid
    deactivate DB
    Auth->>Auth: Generate new access token
    Auth-->>FE: New access token
    deactivate Auth
    FE->>FE: Update stored token
```

**Alternative - Styled Version**:
```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#4F46E5',
  'primaryTextColor':'#fff',
  'primaryBorderColor':'#3730A3',
  'lineColor':'#6366F1',
  'secondaryColor':'#10B981',
  'tertiaryColor':'#F59E0B'
}}}%%
sequenceDiagram
    [Same diagram content with styling]
```

**Bonus - Architecture Diagram**:
```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Frontend["Frontend Layer"]
        React[React SPA]
        Auth_UI[Auth UI Components]
    end

    subgraph Backend["Backend Layer"]
        Auth_Server[Auth Server<br/>OAuth2]
        Resource_Server[Resource Server<br/>API]
        Gateway[API Gateway]
    end

    subgraph Data["Data Layer"]
        UserDB[(User Database)]
        TokenDB[(Token Store)]
        AppDB[(Application DB)]
    end

    Browser --> React
    Mobile --> React
    React --> Auth_UI
    Auth_UI --> Gateway
    Gateway --> Auth_Server
    Gateway --> Resource_Server

    Auth_Server --> UserDB
    Auth_Server --> TokenDB
    Resource_Server --> AppDB
    Resource_Server -.Validates.-> Auth_Server

    style Auth_Server fill:#4F46E5,color:#fff
    style Resource_Server fill:#10B981,color:#fff
    style Gateway fill:#F59E0B,color:#fff
```

---

## 🔍 Code Review Workflows

### Workflow 1: Simple Code Review

**Scenario**: Review a single file before commit

**Agents**: `architect-reviewer`

**Command**:
```bash
/review-simple src/payment_processor.py
```

**Workflow**:
```
1. User invokes command
   ↓
2. architect-reviewer agent
   - Analyzes file
   - Checks patterns
   - Reviews SOLID principles
   ↓
3. Results returned to user
```

**Example Output**:
```markdown
# Code Review: payment_processor.py

## Summary
**Overall Score**: 72/100
**Critical Issues**: 1
**Warnings**: 3
**Suggestions**: 5

## Critical Issues

### 1. God Object Pattern
**Line**: 1-450
**Severity**: High
**Issue**: PaymentProcessor class is 450 lines and handles too many responsibilities
**Impact**: Difficult to test, maintain, and extend
**Recommendation**: Split into:
- PaymentValidator
- PaymentExecutor
- PaymentLogger
- PaymentNotifier
**Effort**: 6-8 hours

## Warnings

### 1. Missing Error Handling
**Line**: 145-160
**Issue**: No try-catch around external payment gateway call
**Recommendation**: Add error handling with retry logic

### 2. Hardcoded Configuration
**Line**: 23
**Issue**: Payment gateway URL hardcoded
**Recommendation**: Move to configuration file

### 3. Missing Type Hints
**Line**: 89-110
**Issue**: Several methods lack type hints
**Recommendation**: Add type hints for better IDE support

## Suggestions

1. Add logging for payment attempts (line 145)
2. Implement circuit breaker pattern for gateway calls
3. Add metrics for payment success/failure rates
4. Consider async processing for large payments
5. Add integration tests for payment flows

## Positive Aspects

✅ Good separation between validation and execution
✅ Clear method names
✅ Appropriate use of enums for payment status
✅ Database transactions properly handled
```

---

### Workflow 2: Comprehensive Code Review

**Scenario**: Full code review with testing and documentation check

**Agents**: `architect-reviewer`, `validation-gates`, `documentation-manager`

**Command**:
```bash
/review-complete
```

**Workflow**:
```
User invokes command
   ↓
Parallel execution:
├─ architect-reviewer
│  └─ Architecture analysis
├─ validation-gates
│  └─ Run all tests
└─ documentation-manager
   └─ Check docs updated
   ↓
Aggregate results
   ↓
Present comprehensive report
```

**Complete Example**:

**Input**: Recent changes to authentication system
```bash
$ git diff --name-only
src/auth/login.py
src/auth/token.py
tests/test_auth.py
```

**Invocation**:
```bash
/review-complete
```

**Agent Outputs**:

**1. architect-reviewer Result**:
```markdown
# Architecture Review

## Impact Assessment: HIGH
Authentication is a critical security boundary.

## Pattern Compliance
✅ Service layer pattern correctly applied
✅ Repository pattern for database access
⚠️ Missing event publishing for login attempts
❌ Direct dependency on concrete TokenGenerator

## SOLID Principles
✅ Single Responsibility: Good separation
❌ Dependency Inversion: Depends on concrete class
⚠️ Open/Closed: Token generation not extensible

## Recommendations
1. Introduce LoginAttemptEvent for audit trail
2. Use dependency injection for TokenGenerator
3. Add interface for token generation strategy

## Estimated Refactoring: 3-4 hours
```

**2. validation-gates Result**:
```bash
# Running validation checks...

$ ruff check .
✅ No linting errors

$ mypy .
✅ Type checking passed

$ pytest -v --cov
======================== test session starts ========================
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_token_generation PASSED
tests/test_auth.py::test_token_expiration PASSED

---------- coverage: platform linux, python 3.11 -----------
Name                    Stmts   Miss  Cover
-------------------------------------------
src/auth/login.py          45      2    96%
src/auth/token.py          32      1    97%
-------------------------------------------
TOTAL                      77      3    96%

======================== 4 passed in 1.85s ==========================

✅ All validation gates passed
✅ Test coverage: 96% (target: 90%)
✅ All tests passing
```

**3. documentation-manager Result**:
```markdown
# Documentation Review

## Files Checked
- README.md
- docs/authentication.md
- API.md

## Updates Needed

### HIGH Priority
❌ API.md missing new login endpoint documentation
   File: API.md
   Action: Add POST /auth/login endpoint

### MEDIUM Priority
⚠️ docs/authentication.md doesn't mention token refresh
   File: docs/authentication.md
   Action: Add section on token refresh flow

### LOW Priority
ℹ️ README.md could mention new auth features
   File: README.md
   Action: Update features list

## Updates Applied
✅ Added login endpoint to API.md
✅ Updated authentication.md with token refresh
✅ Updated README features list

## Documentation Status
All documentation now synchronized with code changes.
```

**Aggregated Report**:
```markdown
# Comprehensive Code Review Report

## Executive Summary
**Overall Status**: ✅ APPROVED with minor recommendations
**Critical Issues**: 0
**Test Coverage**: 96% ✅
**Documentation**: ✅ Updated

## Architecture Review
- **Score**: 82/100
- **Critical Issues**: 1 (dependency injection)
- **Recommendations**: 3 improvements suggested
- **Effort**: 3-4 hours for refactoring

## Quality Validation
- **Linting**: ✅ Pass
- **Type Checking**: ✅ Pass
- **Tests**: ✅ 4/4 passing
- **Coverage**: ✅ 96% (exceeds 90% target)

## Documentation
- **Status**: ✅ Updated
- **Files Updated**: 3
- **Completeness**: ✅ All necessary docs updated

## Recommendations

### Immediate (Before Merge)
None - code is ready to merge

### Short Term (Next Sprint)
1. Implement dependency injection for TokenGenerator
2. Add event publishing for login attempts
3. Make token generation strategy extensible

### Long Term
1. Consider adding metrics for authentication rates
2. Implement rate limiting for login attempts
3. Add integration tests for auth flows

## Approval
✅ Code approved for merge
- All tests passing
- Documentation updated
- No critical issues
- Minor improvements can be addressed in future PRs
```

---

## 📚 Documentation Generation Workflows

### Workflow 1: Quick README Update

**Scenario**: New feature added, update README

**Agents**: `documentation-manager`

**Invocation**:
```
"Use documentation-manager agent to update README.md with the new rate limiting feature added in src/middleware/rate_limit.py"
```

**Output**:
```markdown
# README.md (Updated sections)

## Features

- User authentication with JWT
- RESTful API design
- **Rate limiting middleware** ← NEW
- Database migrations with Alembic
- Comprehensive test coverage

## Configuration

### Rate Limiting

Configure rate limiting in `config.py`:

```python
RATE_LIMIT = {
    "default": "100/hour",
    "auth": "10/minute",
    "api": "1000/hour"
}
```

Usage:
```python
from middleware import rate_limit

@app.route("/api/data")
@rate_limit("api")
def get_data():
    return {"data": "..."}
```

## Installation

```bash
pip install -r requirements.txt

# Rate limiting requires Redis
docker run -d -p 6379:6379 redis
```

## Dependencies

- Flask 2.3+
- SQLAlchemy 2.0+
- **Redis 7.0+** ← NEW (for rate limiting)
```

---

### Workflow 2: Complete System Documentation

**Scenario**: Document entire system for new team members

**Agents**: `docs-architect`, `api-documenter`, `tutorial-engineer`, `mermaid-expert`

**Command**:
```bash
/document-system
```

**Workflow**:
```
User invokes command
   ↓
1. docs-architect (main coordinator)
   - Analyzes codebase structure
   - Plans documentation structure
   ↓
2. Parallel generation:
   ├─ api-documenter → API Reference
   ├─ tutorial-engineer → Getting Started
   └─ mermaid-expert → Architecture Diagrams
   ↓
3. docs-architect assembles complete documentation
   ↓
4. Results written to docs/ directory
```

**Generated Structure**:
```
docs/
├── README.md (index)
├── ARCHITECTURE.md (system overview)
├── GETTING_STARTED.md (tutorial)
├── API_REFERENCE.md (complete API docs)
├── CONFIGURATION.md (configuration guide)
├── DEPLOYMENT.md (deployment guide)
└── diagrams/
    ├── architecture.mmd
    ├── auth-flow.mmd
    └── data-flow.mmd
```

**Sample Output - ARCHITECTURE.md** (generated by docs-architect):
```markdown
# System Architecture

## Executive Summary

This document provides a comprehensive overview of the E-Commerce Platform architecture, design decisions, and implementation details.

**System Type**: Microservices
**Primary Language**: Python 3.11
**Framework**: FastAPI
**Database**: PostgreSQL 15
**Caching**: Redis 7
**Message Queue**: RabbitMQ

## Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph External
        Users[Users]
        Admin[Admin Users]
    end

    subgraph Frontend
        Web[Web Application]
        Mobile[Mobile Apps]
    end

    subgraph API_Gateway
        Gateway[API Gateway<br/>Kong]
    end

    subgraph Services
        Auth[Auth Service]
        Products[Product Service]
        Orders[Order Service]
        Payments[Payment Service]
    end

    subgraph Data
        PG[(PostgreSQL)]
        Redis[(Redis Cache)]
        RabbitMQ[/RabbitMQ\]
    end

    Users --> Web
    Users --> Mobile
    Admin --> Web

    Web --> Gateway
    Mobile --> Gateway

    Gateway --> Auth
    Gateway --> Products
    Gateway --> Orders
    Gateway --> Payments

    Auth --> PG
    Products --> PG
    Orders --> PG
    Payments --> PG

    Products --> Redis
    Orders --> RabbitMQ
    Payments --> RabbitMQ
```

### Component Responsibilities

#### API Gateway (Kong)
- Request routing
- Authentication validation
- Rate limiting
- API versioning
- Request/response transformation

#### Auth Service
- User authentication
- JWT token generation/validation
- Password management
- Session management
- OAuth2 integration

#### Product Service
- Product catalog management
- Inventory tracking
- Search functionality
- Product recommendations
- Cache management

#### Order Service
- Order processing
- Order history
- Order status tracking
- Inventory reservation
- Event publishing

#### Payment Service
- Payment processing
- Payment gateway integration
- Transaction logging
- Refund processing
- PCI compliance

## Design Decisions

### ADR-001: Microservices Architecture

**Status**: Accepted

**Context**: Need scalability and independent deployment

**Decision**: Implement microservices architecture with service-per-bounded-context pattern

**Consequences**:
- ✅ Independent scaling
- ✅ Technology diversity
- ✅ Fault isolation
- ❌ Increased complexity
- ❌ Distributed transaction challenges

### ADR-002: Event-Driven Communication

**Status**: Accepted

**Context**: Services need to communicate asynchronously

**Decision**: Use RabbitMQ for inter-service events

**Consequences**:
- ✅ Loose coupling
- ✅ Better fault tolerance
- ❌ Eventual consistency
- ❌ Debugging complexity

## Core Components

### Authentication Flow

[Detailed authentication implementation...]

### Database Schema

[Complete schema documentation...]

### API Endpoints

[API reference with examples...]

[... continues for 50+ pages]
```

---

## 🔄 Multi-Agent Coordination Patterns

### Pattern 1: Research → Implement → Validate

**Scenario**: Implement new feature based on best practices

**Agents**: `search-specialist`, `python-pro`, `validation-gates`

**Command**:
```bash
/research-implement "Add caching layer with Redis"
```

**Workflow**:
```
1. search-specialist
   - Research Redis caching patterns
   - Find best practices
   - Identify Python libraries
   ↓
2. python-pro (uses research)
   - Implement caching layer
   - Add Redis client
   - Create cache decorator
   ↓
3. validation-gates
   - Test implementation
   - Verify performance
   - Ensure tests pass
```

**Detailed Example**:

**Step 1: search-specialist Output**:
```markdown
# Research: Redis Caching Patterns

## Key Findings

### Best Practices
1. **Connection Pooling**: Use connection pools (redis-py ConnectionPool)
2. **Serialization**: Use pickle or msgpack for Python objects
3. **TTL Strategy**: Set appropriate expiration times
4. **Cache Invalidation**: Implement cache invalidation on updates
5. **Error Handling**: Gracefully degrade if Redis unavailable

### Recommended Library
**redis-py**: Official Redis client for Python
- Mature and well-maintained
- Connection pooling built-in
- Async support available

### Implementation Pattern
```python
import redis
from functools import wraps

# Create connection pool
redis_client = redis.ConnectionPool(host='localhost', port=6379)

# Cache decorator pattern
def cache(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(key)
            if cached:
                return pickle.loads(cached)

            result = func(*args, **kwargs)
            redis_client.setex(key, ttl, pickle.dumps(result))
            return result
        return wrapper
    return decorator
```

## Performance Benchmarks
- Cache hit: ~0.1ms
- Cache miss + DB query: ~50ms
- **Speedup**: 500x for cached data
```

**Step 2: python-pro Output** (using research):
```python
# cache.py - Production-ready caching implementation
import pickle
import logging
from functools import wraps
from typing import Any, Callable, Optional, Union
import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)

class CacheError(Exception):
    """Raised when cache operation fails."""
    pass

class Cache:
    """Redis cache client with connection pooling and error handling."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 50
    ):
        """Initialize cache client with connection pool.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            max_connections: Maximum connections in pool
        """
        try:
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                max_connections=max_connections,
                decode_responses=False  # We handle serialization
            )
            self.client = redis.Redis(connection_pool=self.pool)
            # Test connection
            self.client.ping()
            logger.info(f"Cache connected to {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Cache connection failed: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        Raises:
            CacheError: If cache operation fails
        """
        try:
            value = self.client.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                return None

            logger.debug(f"Cache hit: {key}")
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            raise CacheError(f"Failed to get {key}: {e}")

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful

        Raises:
            CacheError: If cache operation fails
        """
        try:
            serialized = pickle.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)

            logger.debug(f"Cache set: {key} (ttl={ttl})")
            return True
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            raise CacheError(f"Failed to set {key}: {e}")

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        try:
            result = self.client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if successful
        """
        try:
            self.client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False

def cached(
    ttl: int = 300,
    key_prefix: str = "",
    cache_client: Optional[Cache] = None
) -> Callable:
    """Decorator to cache function results.

    Args:
        ttl: Cache time-to-live in seconds
        key_prefix: Prefix for cache keys
        cache_client: Cache instance (uses default if None)

    Returns:
        Decorated function with caching

    Example:
        ```python
        @cached(ttl=600)
        def expensive_query(user_id: int):
            return db.query(User).get(user_id)
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache client
            client = cache_client or get_default_cache()

            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.append(str(args))
            if kwargs:
                key_parts.append(str(sorted(kwargs.items())))
            cache_key = ":".join(filter(None, key_parts))

            # Try to get from cache
            try:
                cached_result = client.get(cache_key)
                if cached_result is not None:
                    return cached_result
            except CacheError as e:
                logger.warning(f"Cache get failed, executing function: {e}")

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            try:
                client.set(cache_key, result, ttl=ttl)
            except CacheError as e:
                logger.warning(f"Cache set failed: {e}")

            return result
        return wrapper
    return decorator

# Global cache instance
_default_cache: Optional[Cache] = None

def get_default_cache() -> Cache:
    """Get or create default cache instance."""
    global _default_cache
    if _default_cache is None:
        _default_cache = Cache()
    return _default_cache


# Usage example
@cached(ttl=600, key_prefix="user")
def get_user(user_id: int):
    """Get user from database with caching."""
    return db.query(User).filter(User.id == user_id).first()
```

**Step 3: validation-gates Output**:
```python
# tests/test_cache.py - Comprehensive tests
import pytest
import time
from unittest.mock import Mock, patch
from cache import Cache, cached, CacheError

class TestCache:
    """Tests for Cache class."""

    @pytest.fixture
    def cache(self):
        """Create test cache instance."""
        return Cache(db=1)  # Use different DB for tests

    @pytest.fixture(autouse=True)
    def cleanup(self, cache):
        """Clean up cache after each test."""
        yield
        cache.clear()

    def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_get_nonexistent_key(self, cache):
        """Test get returns None for missing key."""
        assert cache.get("nonexistent") is None

    def test_set_with_ttl_expires(self, cache):
        """Test TTL causes key to expire."""
        cache.set("temp_key", "temp_value", ttl=1)
        assert cache.get("temp_key") == "temp_value"

        time.sleep(1.1)
        assert cache.get("temp_key") is None

    def test_delete(self, cache):
        """Test delete removes key."""
        cache.set("delete_me", "value")
        assert cache.delete("delete_me") is True
        assert cache.get("delete_me") is None

    def test_cache_complex_objects(self, cache):
        """Test caching complex Python objects."""
        obj = {"nested": {"data": [1, 2, 3]}, "count": 42}
        cache.set("complex", obj)
        assert cache.get("complex") == obj

class TestCachedDecorator:
    """Tests for @cached decorator."""

    @pytest.fixture
    def cache(self):
        cache = Cache(db=1)
        yield cache
        cache.clear()

    def test_caches_result(self, cache):
        """Test decorator caches function result."""
        call_count = 0

        @cached(ttl=10, cache_client=cache)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call - cache miss
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - cache hit
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Function not called again

    def test_different_args_different_cache(self, cache):
        """Test different arguments use different cache keys."""
        @cached(ttl=10, cache_client=cache)
        def func(x):
            return x * 2

        assert func(5) == 10
        assert func(10) == 20  # Different arg, different result

    def test_graceful_degradation_on_cache_failure(self, cache):
        """Test function still works if cache fails."""
        @cached(ttl=10, cache_client=cache)
        def func(x):
            return x * 2

        # Simulate cache failure
        with patch.object(cache, 'get', side_effect=CacheError("Connection failed")):
            result = func(5)
            assert result == 10  # Function still executes

# Run tests
$ pytest tests/test_cache.py -v --cov=cache
======================== test session starts ========================
tests/test_cache.py::TestCache::test_set_and_get PASSED
tests/test_cache.py::TestCache::test_get_nonexistent_key PASSED
tests/test_cache.py::TestCache::test_set_with_ttl_expires PASSED
tests/test_cache.py::TestCache::test_delete PASSED
tests/test_cache.py::TestCache::test_cache_complex_objects PASSED
tests/test_cache.py::TestCachedDecorator::test_caches_result PASSED
tests/test_cache.py::TestCachedDecorator::test_different_args_different_cache PASSED
tests/test_cache.py::TestCachedDecorator::test_graceful_degradation_on_cache_failure PASSED

---------- coverage: platform linux, python 3.11 -----------
Name        Stmts   Miss  Cover
-------------------------------
cache.py      120      5    96%
-------------------------------

======================== 8 passed in 2.15s ==========================

✅ All tests passed!
✅ Coverage: 96%
✅ Implementation validated
```

---

## 🔗 Related Documentation

### Essential Reading

| Document | Purpose |
|----------|---------|
| [Agents README](./README.md) | Overview and quick start |
| [Agent Architecture](./agent-architecture.md) | System architecture |
| [Agent Catalog](./agent-catalog.md) | All available agents |
| [Creating Agents](./creating-agents.md) | Build custom agents |

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: Agent System Team
**Status**: Active

---

**Navigate**: [← Back to Agents](./README.md) | [Creating Agents ←](./creating-agents.md) | [Agent Catalog ←](./agent-catalog.md)

---

*Real-world examples demonstrating the power of multi-agent workflows*
