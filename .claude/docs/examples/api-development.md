# API Development Examples

## Complete API Development Workflow

This guide demonstrates comprehensive API development using the Claude Code Context Engineering system, from requirements gathering through implementation, testing, and documentation.

## Table of Contents

1. [Hello World API](#hello-world)
2. [RESTful CRUD API](#restful-crud)
3. [Microservices Architecture](#microservices)
4. [GraphQL API](#graphql-api)
5. [WebSocket Real-time API](#websocket-api)
6. [Full Stack Application](#full-stack)
7. [API Security](#api-security)
8. [Performance Optimization](#performance)

## Hello World

### Simple FastAPI Application

#### Step 1: Initialize Project

```bash
# Start new API project
/task-next "Create a simple Hello World API with FastAPI"

# System response:
# ✓ Analyzing requirements...
# ✓ Creating project structure...
# ✓ Generating initial code...
```

#### Step 2: Generated Code

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="Hello World API",
    description="A simple API demonstration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class HelloResponse(BaseModel):
    message: str
    name: Optional[str] = None
    timestamp: str

class HelloRequest(BaseModel):
    name: str

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Hello World API"}

@app.get("/hello")
async def hello_world():
    """Simple hello endpoint"""
    from datetime import datetime
    return HelloResponse(
        message="Hello, World!",
        timestamp=datetime.now().isoformat()
    )

@app.post("/hello")
async def hello_name(request: HelloRequest):
    """Personalized hello endpoint"""
    from datetime import datetime
    return HelloResponse(
        message=f"Hello, {request.name}!",
        name=request.name,
        timestamp=datetime.now().isoformat()
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "hello-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

#### Step 3: Test the API

```bash
# Run the API
python main.py

# Test with curl
curl http://localhost:8000/
# {"message":"Welcome to Hello World API"}

curl http://localhost:8000/hello
# {"message":"Hello, World!","name":null,"timestamp":"2024-01-15T10:30:00"}

curl -X POST http://localhost:8000/hello \
  -H "Content-Type: application/json" \
  -d '{"name":"Claude"}'
# {"message":"Hello, Claude!","name":"Claude","timestamp":"2024-01-15T10:31:00"}
```

#### Step 4: Add Tests

```python
# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Hello World API"

def test_hello_world():
    response = client.get("/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, World!"
    assert "timestamp" in data

def test_hello_name():
    response = client.post("/hello", json={"name": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, Test!"
    assert data["name"] == "Test"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

```bash
# Run tests
pytest test_main.py -v

# Output:
# test_main.py::test_root PASSED
# test_main.py::test_hello_world PASSED
# test_main.py::test_hello_name PASSED
# test_main.py::test_health PASSED
# ======================== 4 passed in 0.25s ========================
```

## RESTful CRUD

### Complete CRUD API with Database

#### Step 1: Requirements Gathering

```bash
# Use task command to define requirements
/task-next "Create a RESTful CRUD API for a book management system"

# Follow-up prompts:
# > Database preference? PostgreSQL
# > Authentication required? Yes, JWT
# > Need pagination? Yes
# > Need filtering/search? Yes
```

#### Step 2: Database Models

```python
# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Model
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    isbn = Column(String(13), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    published_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models
class BookBase(BaseModel):
    title: str = Field(..., max_length=200)
    author: str = Field(..., max_length=100)
    isbn: str = Field(..., regex="^[0-9]{13}$")
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    published_date: Optional[datetime] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    published_date: Optional[datetime] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    size: int
    pages: int
```

#### Step 3: API Implementation

```python
# api.py
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/books")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Management API", version="1.0.0")
security = HTTPBearer()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# CRUD Operations
class BookService:
    @staticmethod
    def create_book(db: Session, book: BookCreate) -> Book:
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def get_book(db: Session, book_id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def get_books(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> List[Book]:
        query = db.query(Book)
        if search:
            search_filter = or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                Book.isbn.like(f"%{search}%")
            )
            query = query.filter(search_filter)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_book(db: Session, book_id: int, book: BookUpdate) -> Optional[Book]:
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if db_book:
            for key, value in book.dict(exclude_unset=True).items():
                setattr(db_book, key, value)
            db.commit()
            db.refresh(db_book)
        return db_book

    @staticmethod
    def delete_book(db: Session, book_id: int) -> bool:
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if db_book:
            db.delete(db_book)
            db.commit()
            return True
        return False

# API Endpoints
@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Create a new book"""
    return BookService.create_book(db, book)

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get a specific book by ID"""
    book = BookService.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books", response_model=PaginatedResponse)
async def get_books(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of books with optional search"""
    skip = (page - 1) * size
    books = BookService.get_books(db, skip, size, search)

    # Get total count
    total_query = db.query(Book)
    if search:
        search_filter = or_(
            Book.title.ilike(f"%{search}%"),
            Book.author.ilike(f"%{search}%")
        )
        total_query = total_query.filter(search_filter)
    total = total_query.count()

    return PaginatedResponse(
        items=books,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int = Path(..., gt=0),
    book: BookUpdate = ...,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Update a book"""
    updated_book = BookService.update_book(db, book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@app.delete("/books/{book_id}", status_code=204)
async def delete_book(
    book_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Delete a book"""
    if not BookService.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
```

#### Step 4: API Testing

```python
# test_crud.py
import pytest
from fastapi.testclient import TestClient
from api import app
import json

client = TestClient(app)

# Mock JWT token for testing
TEST_TOKEN = "Bearer test_token_here"

@pytest.fixture
def book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "price": 29.99,
        "description": "A test book"
    }

def test_create_book(book_data):
    response = client.post(
        "/books",
        json=book_data,
        headers={"Authorization": TEST_TOKEN}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == book_data["title"]
    assert "id" in data
    return data["id"]

def test_get_book():
    book_id = 1  # Assuming book was created
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data

def test_get_books_paginated():
    response = client.get("/books?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data

def test_search_books():
    response = client.get("/books?search=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)

def test_update_book():
    book_id = 1
    update_data = {"price": 34.99}
    response = client.put(
        f"/books/{book_id}",
        json=update_data,
        headers={"Authorization": TEST_TOKEN}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 34.99

def test_delete_book():
    book_id = 1
    response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": TEST_TOKEN}
    )
    assert response.status_code == 204
```

## Microservices

### Microservices Architecture Implementation

#### Step 1: Service Design

```bash
# Design microservices architecture
/research-topic "Microservices best practices for e-commerce"

# Generate service structure
/agent-start architect
/agent-task "Design microservices for e-commerce platform"
```

#### Step 2: Service Implementation

```python
# user_service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import httpx
import asyncio
from typing import Optional

app = FastAPI(title="User Service", version="1.0.0")

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    full_name: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

# Service Registry
SERVICE_REGISTRY = {
    "auth": "http://auth-service:3000",
    "notification": "http://notification-service:3001",
    "order": "http://order-service:3002"
}

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create new user and trigger related services"""

    # Create user in database
    new_user = User(
        id=1,  # Generated ID
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )

    # Notify other services asynchronously
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(f"{SERVICE_REGISTRY['auth']}/register", json={
                "user_id": new_user.id,
                "username": user.username,
                "password": user.password
            }),
            client.post(f"{SERVICE_REGISTRY['notification']}/welcome", json={
                "user_id": new_user.id,
                "email": user.email,
                "name": user.full_name
            })
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    return new_user

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user with aggregated data from other services"""

    # Get base user data
    user_data = {
        "id": user_id,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe"
    }

    # Aggregate data from other services
    async with httpx.AsyncClient() as client:
        try:
            # Get order history
            orders_response = await client.get(
                f"{SERVICE_REGISTRY['order']}/users/{user_id}/orders"
            )
            user_data["orders"] = orders_response.json() if orders_response.status_code == 200 else []
        except:
            user_data["orders"] = []

    return user_data
```

```python
# order_service/main.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import httpx

app = FastAPI(title="Order Service", version="1.0.0")

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Order(BaseModel):
    id: Optional[int] = None
    user_id: int
    items: List[OrderItem]
    total: float
    status: str = "pending"
    created_at: Optional[datetime] = None

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]

# Event publishing
async def publish_event(event_type: str, data: dict):
    """Publish events to event bus"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://event-bus:3003/publish",
            json={"type": event_type, "data": data}
        )

@app.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks
):
    """Create order and trigger fulfillment process"""

    # Calculate total
    total = sum(item.quantity * item.price for item in order.items)

    # Create order
    new_order = Order(
        id=1,  # Generated ID
        user_id=order.user_id,
        items=order.items,
        total=total,
        created_at=datetime.now()
    )

    # Publish order created event
    background_tasks.add_task(
        publish_event,
        "order.created",
        new_order.dict()
    )

    return new_order

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Get order details"""
    # Return mock order for example
    return Order(
        id=order_id,
        user_id=1,
        items=[
            OrderItem(product_id=1, quantity=2, price=29.99),
            OrderItem(product_id=2, quantity=1, price=49.99)
        ],
        total=109.97,
        status="processing",
        created_at=datetime.now()
    )

@app.get("/users/{user_id}/orders", response_model=List[Order])
async def get_user_orders(user_id: int):
    """Get all orders for a user"""
    return [
        Order(
            id=1,
            user_id=user_id,
            items=[OrderItem(product_id=1, quantity=1, price=29.99)],
            total=29.99,
            status="delivered",
            created_at=datetime.now()
        )
    ]
```

#### Step 3: API Gateway

```python
# gateway/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import asyncio
from typing import Dict, Any

app = FastAPI(title="API Gateway", version="1.0.0")

# Service routing configuration
ROUTES = {
    "/api/users": "http://user-service:3000",
    "/api/orders": "http://order-service:3002",
    "/api/products": "http://product-service:3004",
    "/api/auth": "http://auth-service:3001"
}

# Circuit breaker implementation
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = {}
        self.last_failure = {}

    def is_open(self, service: str) -> bool:
        if service not in self.failures:
            return False

        import time
        if self.failures[service] >= self.threshold:
            if time.time() - self.last_failure[service] < self.timeout:
                return True
            else:
                self.failures[service] = 0
        return False

    def record_failure(self, service: str):
        import time
        self.failures[service] = self.failures.get(service, 0) + 1
        self.last_failure[service] = time.time()

    def record_success(self, service: str):
        self.failures[service] = 0

circuit_breaker = CircuitBreaker()

@app.middleware("http")
async def route_request(request: Request, call_next):
    """Route requests to appropriate microservice"""

    path = request.url.path

    # Find matching route
    service_url = None
    for route_prefix, service in ROUTES.items():
        if path.startswith(route_prefix):
            service_url = service
            break

    if not service_url:
        return await call_next(request)

    # Check circuit breaker
    if circuit_breaker.is_open(service_url):
        return JSONResponse(
            status_code=503,
            content={"error": "Service temporarily unavailable"}
        )

    # Forward request to microservice
    try:
        async with httpx.AsyncClient() as client:
            # Build target URL
            target_url = f"{service_url}{path.replace(route_prefix, '')}"

            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers,
                content=await request.body()
            )

            circuit_breaker.record_success(service_url)

            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )

    except Exception as e:
        circuit_breaker.record_failure(service_url)
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/health")
async def health_check():
    """Check health of all services"""

    health_status = {}

    async def check_service(name: str, url: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                health_status[name] = response.status_code == 200
        except:
            health_status[name] = False

    # Check all services in parallel
    tasks = [
        check_service(name.replace("/api/", ""), url)
        for name, url in ROUTES.items()
    ]
    await asyncio.gather(*tasks)

    all_healthy = all(health_status.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": health_status
    }
```

#### Step 4: Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  user-service:
    build: ./user_service
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/users
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  order-service:
    build: ./order_service
    ports:
      - "3002:3002"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/orders
      - EVENT_BUS_URL=http://event-bus:3003
    depends_on:
      - postgres
      - event-bus

  auth-service:
    build: ./auth_service
    ports:
      - "3001:3001"
    environment:
      - JWT_SECRET=your-secret-key
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  api-gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    depends_on:
      - user-service
      - order-service
      - auth-service

  event-bus:
    build: ./event_bus
    ports:
      - "3003:3003"
    environment:
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=microservices
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres_data:
```

## GraphQL API

### Complete GraphQL Implementation

#### Step 1: Schema Definition

```python
# schema.py
import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class User:
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime
    posts: List["Post"]

@strawberry.type
class Post:
    id: int
    title: str
    content: str
    author: User
    published: bool
    created_at: datetime
    updated_at: Optional[datetime]
    comments: List["Comment"]

@strawberry.type
class Comment:
    id: int
    content: str
    author: User
    post: Post
    created_at: datetime

@strawberry.input
class CreateUserInput:
    username: str
    email: str
    full_name: str

@strawberry.input
class CreatePostInput:
    title: str
    content: str
    author_id: int
    published: bool = False

@strawberry.input
class UpdatePostInput:
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
```

#### Step 2: Resolvers

```python
# resolvers.py
import strawberry
from typing import List, Optional
from schema import User, Post, Comment, CreateUserInput, CreatePostInput, UpdatePostInput

@strawberry.type
class Query:
    @strawberry.field
    async def users(self, limit: Optional[int] = 10) -> List[User]:
        """Get all users"""
        # Fetch from database
        return await get_users_from_db(limit)

    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """Get user by ID"""
        return await get_user_by_id(id)

    @strawberry.field
    async def posts(
        self,
        published: Optional[bool] = None,
        author_id: Optional[int] = None,
        limit: Optional[int] = 20
    ) -> List[Post]:
        """Get posts with filters"""
        return await get_posts(published, author_id, limit)

    @strawberry.field
    async def post(self, id: int) -> Optional[Post]:
        """Get post by ID"""
        return await get_post_by_id(id)

    @strawberry.field
    async def search_posts(self, query: str) -> List[Post]:
        """Search posts by title or content"""
        return await search_posts_in_db(query)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> User:
        """Create a new user"""
        user_data = {
            "username": input.username,
            "email": input.email,
            "full_name": input.full_name
        }
        return await create_user_in_db(user_data)

    @strawberry.mutation
    async def create_post(self, input: CreatePostInput) -> Post:
        """Create a new post"""
        post_data = {
            "title": input.title,
            "content": input.content,
            "author_id": input.author_id,
            "published": input.published
        }
        return await create_post_in_db(post_data)

    @strawberry.mutation
    async def update_post(self, id: int, input: UpdatePostInput) -> Optional[Post]:
        """Update an existing post"""
        updates = {}
        if input.title is not None:
            updates["title"] = input.title
        if input.content is not None:
            updates["content"] = input.content
        if input.published is not None:
            updates["published"] = input.published

        return await update_post_in_db(id, updates)

    @strawberry.mutation
    async def delete_post(self, id: int) -> bool:
        """Delete a post"""
        return await delete_post_from_db(id)

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def post_created(self) -> Post:
        """Subscribe to new posts"""
        async for post in post_created_stream():
            yield post

    @strawberry.subscription
    async def comment_added(self, post_id: int) -> Comment:
        """Subscribe to comments on a specific post"""
        async for comment in comment_stream(post_id):
            yield comment
```

#### Step 3: GraphQL Server

```python
# graphql_app.py
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

# Create FastAPI app
app = FastAPI(title="GraphQL API")

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Add router to app
app.include_router(graphql_app, prefix="/graphql")

# Add REST endpoint for health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Step 4: GraphQL Queries

```graphql
# Example queries

# Get all users with their posts
query GetUsers {
  users(limit: 10) {
    id
    username
    email
    posts {
      id
      title
      published
    }
  }
}

# Get specific post with comments
query GetPost($postId: Int!) {
  post(id: $postId) {
    id
    title
    content
    author {
      username
    }
    comments {
      id
      content
      author {
        username
      }
    }
  }
}

# Search posts
query SearchPosts($searchQuery: String!) {
  searchPosts(query: $searchQuery) {
    id
    title
    content
    author {
      username
    }
  }
}

# Create a new post
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    content
    published
    createdAt
  }
}

# Update post
mutation UpdatePost($id: Int!, $input: UpdatePostInput!) {
  updatePost(id: $id, input: $input) {
    id
    title
    content
    published
    updatedAt
  }
}

# Subscribe to new posts
subscription OnPostCreated {
  postCreated {
    id
    title
    author {
      username
    }
  }
}
```

## WebSocket API

### Real-time WebSocket Implementation

#### Step 1: WebSocket Server

```python
# websocket_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

app = FastAPI(title="WebSocket Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, Set[str]] = {}
        self.room_users: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await self.send_personal_message(
            {"type": "connection", "message": "Connected successfully"},
            user_id
        )

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Remove from all rooms
        if user_id in self.user_rooms:
            for room in self.user_rooms[user_id]:
                if room in self.room_users:
                    self.room_users[room].discard(user_id)
            del self.user_rooms[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast_to_room(self, message: dict, room_id: str):
        if room_id in self.room_users:
            tasks = []
            for user_id in self.room_users[room_id]:
                if user_id in self.active_connections:
                    tasks.append(
                        self.active_connections[user_id].send_json(message)
                    )
            await asyncio.gather(*tasks, return_exceptions=True)

    async def join_room(self, user_id: str, room_id: str):
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)

        if room_id not in self.room_users:
            self.room_users[room_id] = set()
        self.room_users[room_id].add(user_id)

        # Notify room members
        await self.broadcast_to_room({
            "type": "user_joined",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.now().isoformat()
        }, room_id)

    async def leave_room(self, user_id: str, room_id: str):
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)

        if room_id in self.room_users:
            self.room_users[room_id].discard(user_id)

        # Notify room members
        await self.broadcast_to_room({
            "type": "user_left",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.now().isoformat()
        }, room_id)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Handle different message types
            if data["type"] == "join_room":
                await manager.join_room(user_id, data["room_id"])

            elif data["type"] == "leave_room":
                await manager.leave_room(user_id, data["room_id"])

            elif data["type"] == "message":
                # Broadcast message to room
                message = {
                    "type": "message",
                    "user_id": user_id,
                    "content": data["content"],
                    "room_id": data["room_id"],
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast_to_room(message, data["room_id"])

            elif data["type"] == "typing":
                # Notify room that user is typing
                notification = {
                    "type": "typing",
                    "user_id": user_id,
                    "room_id": data["room_id"]
                }
                await manager.broadcast_to_room(notification, data["room_id"])

            elif data["type"] == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    user_id
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # Notify all rooms that user disconnected
        for room_id in list(manager.room_users.keys()):
            if user_id in manager.room_users.get(room_id, set()):
                await manager.broadcast_to_room({
                    "type": "user_disconnected",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }, room_id)

@app.get("/rooms")
async def get_rooms():
    """Get list of active rooms"""
    return {
        "rooms": [
            {
                "id": room_id,
                "users": list(users),
                "user_count": len(users)
            }
            for room_id, users in manager.room_users.items()
        ]
    }

@app.get("/users/online")
async def get_online_users():
    """Get list of online users"""
    return {
        "users": list(manager.active_connections.keys()),
        "count": len(manager.active_connections)
    }
```

#### Step 2: WebSocket Client

```javascript
// websocket_client.js
class WebSocketClient {
    constructor(userId) {
        this.userId = userId;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageHandlers = new Map();
        this.currentRoom = null;
    }

    connect() {
        const wsUrl = `ws://localhost:8000/ws/${this.userId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to WebSocket');
            this.reconnectAttempts = 0;
            this.onConnected();
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.attemptReconnect();
        };
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    handleMessage(message) {
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        } else {
            console.log('Unhandled message type:', message.type, message);
        }
    }

    on(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected');
        }
    }

    joinRoom(roomId) {
        this.currentRoom = roomId;
        this.send({
            type: 'join_room',
            room_id: roomId
        });
    }

    leaveRoom(roomId) {
        this.send({
            type: 'leave_room',
            room_id: roomId
        });
        if (this.currentRoom === roomId) {
            this.currentRoom = null;
        }
    }

    sendMessage(content) {
        if (!this.currentRoom) {
            console.error('Not in a room');
            return;
        }

        this.send({
            type: 'message',
            content: content,
            room_id: this.currentRoom
        });
    }

    sendTyping() {
        if (!this.currentRoom) return;

        this.send({
            type: 'typing',
            room_id: this.currentRoom
        });
    }

    ping() {
        this.send({ type: 'ping' });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    onConnected() {
        // Override this method
    }
}

// Usage example
const client = new WebSocketClient('user123');

// Set up message handlers
client.on('connection', (msg) => {
    console.log('Connection confirmed:', msg.message);
});

client.on('message', (msg) => {
    console.log(`[${msg.user_id}]: ${msg.content}`);
    // Update UI
});

client.on('user_joined', (msg) => {
    console.log(`${msg.user_id} joined room ${msg.room_id}`);
});

client.on('user_left', (msg) => {
    console.log(`${msg.user_id} left room ${msg.room_id}`);
});

client.on('typing', (msg) => {
    console.log(`${msg.user_id} is typing...`);
    // Show typing indicator
});

// Connect to server
client.connect();

// Join a room
client.joinRoom('general');

// Send a message
client.sendMessage('Hello, everyone!');

// Send typing notification
client.sendTyping();

// Periodic ping to keep connection alive
setInterval(() => {
    client.ping();
}, 30000);
```

## Full Stack

### Complete Full Stack Application

#### Step 1: Project Structure

```bash
# Initialize full stack project
/full-stack-init "E-commerce Platform" \
  --frontend react \
  --backend fastapi \
  --database postgresql \
  --auth jwt \
  --testing true

# Generated structure:
# ecommerce-platform/
# ├── backend/
# │   ├── app/
# │   │   ├── api/
# │   │   ├── core/
# │   │   ├── models/
# │   │   ├── services/
# │   │   └── schemas/
# │   ├── tests/
# │   └── requirements.txt
# ├── frontend/
# │   ├── src/
# │   │   ├── components/
# │   │   ├── pages/
# │   │   ├── services/
# │   │   └── utils/
# │   ├── public/
# │   └── package.json
# ├── docker-compose.yml
# └── README.md
```

#### Step 2: Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis
from app.core.config import settings
from app.core.database import get_db
from app.api import auth, products, orders, users
from app.core.security import get_current_user

app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "cache": "connected"
    }

# Product service example
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

@app.post("/api/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new product (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    service = ProductService(db)
    return service.create_product(product)

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product by ID with caching"""
    # Check cache first
    cached = redis_client.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)

    service = ProductService(db)
    product = service.get_product(product_id)

    # Cache for 5 minutes
    redis_client.setex(
        f"product:{product_id}",
        300,
        product.json()
    )

    return product
```

#### Step 3: Frontend Implementation

```jsx
// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ProductPage from './pages/ProductPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <div className="App">
            <Navbar />
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products/:id" element={<ProductPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/admin/*" element={<AdminDashboard />} />
            </Routes>
          </div>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
```

```jsx
// frontend/src/services/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await api.post('/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

export const productAPI = {
  getAll: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (product) => api.post('/products', product),
  update: (id, product) => api.put(`/products/${id}`, product),
  delete: (id) => api.delete(`/products/${id}`),
  search: (query) => api.get('/products/search', { params: { q: query } }),
};

export const orderAPI = {
  create: (orderData) => api.post('/orders', orderData),
  getMyOrders: () => api.get('/orders/me'),
  getById: (id) => api.get(`/orders/${id}`),
  updateStatus: (id, status) => api.patch(`/orders/${id}/status`, { status }),
};

export const cartAPI = {
  get: () => api.get('/cart'),
  add: (productId, quantity) => api.post('/cart/items', { product_id: productId, quantity }),
  update: (itemId, quantity) => api.patch(`/cart/items/${itemId}`, { quantity }),
  remove: (itemId) => api.delete(`/cart/items/${itemId}`),
  clear: () => api.delete('/cart'),
};

export default api;
```

```jsx
// frontend/src/components/ProductList.js
import React, { useState, useEffect } from 'react';
import { productAPI } from '../services/api';
import ProductCard from './ProductCard';
import LoadingSpinner from './LoadingSpinner';
import Pagination from './Pagination';

function ProductList({ category, searchQuery }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchProducts();
  }, [category, searchQuery, page]);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page,
        limit: 12,
        ...(category && { category }),
        ...(searchQuery && { search: searchQuery }),
      };

      const response = await productAPI.getAll(params);
      setProducts(response.data.items);
      setTotalPages(response.data.pages);
    } catch (err) {
      setError('Failed to load products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;
  if (products.length === 0) return <div className="no-products">No products found</div>;

  return (
    <div className="product-list">
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

export default ProductList;
```

#### Step 4: Testing

```python
# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from tests.utils import create_test_user, create_test_product

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authenticated user and return headers"""
    user = create_test_user()
    response = client.post("/api/auth/login", json={
        "username": user.username,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_product(auth_headers):
    """Test product creation"""
    product_data = {
        "name": "Test Product",
        "description": "Test description",
        "price": 29.99,
        "stock": 100,
        "category": "Electronics"
    }

    response = client.post(
        "/api/products",
        json=product_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]

def test_get_products():
    """Test getting product list"""
    # Create test products
    for i in range(5):
        create_test_product(name=f"Product {i}")

    response = client.get("/api/products")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 5

def test_search_products():
    """Test product search"""
    create_test_product(name="Laptop")
    create_test_product(name="Desktop")
    create_test_product(name="Phone")

    response = client.get("/api/products/search?q=top")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2  # Laptop and Desktop

def test_order_creation(auth_headers):
    """Test order creation"""
    product = create_test_product()

    order_data = {
        "items": [
            {
                "product_id": product.id,
                "quantity": 2
            }
        ],
        "shipping_address": {
            "street": "123 Main St",
            "city": "Test City",
            "zip": "12345",
            "country": "US"
        }
    }

    response = client.post(
        "/api/orders",
        json=order_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == product.price * 2
```

```javascript
// frontend/src/tests/ProductList.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProductList from '../components/ProductList';
import { productAPI } from '../services/api';

jest.mock('../services/api');

describe('ProductList', () => {
  const mockProducts = [
    { id: 1, name: 'Product 1', price: 10.99 },
    { id: 2, name: 'Product 2', price: 20.99 },
  ];

  beforeEach(() => {
    productAPI.getAll.mockResolvedValue({
      data: {
        items: mockProducts,
        total: 2,
        pages: 1,
      },
    });
  });

  test('renders products', async () => {
    render(<ProductList />);

    await waitFor(() => {
      expect(screen.getByText('Product 1')).toBeInTheDocument();
      expect(screen.getByText('Product 2')).toBeInTheDocument();
    });
  });

  test('shows loading state', () => {
    render(<ProductList />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('handles error state', async () => {
    productAPI.getAll.mockRejectedValue(new Error('API Error'));
    render(<ProductList />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load products')).toBeInTheDocument();
    });
  });

  test('filters by category', async () => {
    render(<ProductList category="Electronics" />);

    await waitFor(() => {
      expect(productAPI.getAll).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'Electronics',
        })
      );
    });
  });
});
```

## API Security

### Comprehensive Security Implementation

#### Authentication & Authorization

```python
# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class SecurityService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None or payload.get("type") != "access":
                raise credentials_exception

            # Get user from database
            user = await get_user_by_username(username)
            if user is None:
                raise credentials_exception

            return user

        except JWTError:
            raise credentials_exception
```

#### Rate Limiting

```python
# rate_limiting.py
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from typing import Callable

# Create limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"]
)

# Redis-based rate limiter for distributed systems
class DistributedRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if rate limit is exceeded"""
        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, window_seconds)

        return current <= max_requests

    def rate_limit_middleware(
        self,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> Callable:
        """Middleware factory for rate limiting"""

        async def middleware(request: Request, call_next):
            # Get client identifier
            client_id = request.client.host
            key = f"rate_limit:{client_id}"

            # Check rate limit
            if not self.check_rate_limit(key, max_requests, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )

            response = await call_next(request)
            return response

        return middleware
```

## Performance

### Performance Optimization Techniques

#### Caching Strategy

```python
# caching.py
from functools import wraps
import hashlib
import json
import redis
from typing import Optional, Any

class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    def delete(self, key: str):
        """Delete key from cache"""
        self.redis.delete(key)

    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)

    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None,
        key_func: Optional[Callable] = None
    ):
        """Decorator for caching function results"""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self.generate_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function
                result = await func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator

# Usage example
cache = CacheService(redis_client)

@cache.cached(prefix="products", ttl=600)
async def get_product_details(product_id: int):
    # Expensive database query
    return await db.query(Product).filter(Product.id == product_id).first()
```

#### Database Optimization

```python
# database_optimization.py
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload, subqueryload

class OptimizedQueries:
    @staticmethod
    async def get_products_with_reviews(db: Session, limit: int = 20):
        """Optimized query with eager loading"""
        return await db.execute(
            select(Product)
            .options(
                selectinload(Product.reviews),
                selectinload(Product.category)
            )
            .limit(limit)
        )

    @staticmethod
    async def get_order_summary(db: Session, user_id: int):
        """Aggregated query for order summary"""
        return await db.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_spent"),
                func.avg(Order.total).label("avg_order_value")
            )
            .where(Order.user_id == user_id)
        )

    @staticmethod
    async def bulk_insert_products(db: Session, products: List[dict]):
        """Bulk insert for better performance"""
        await db.execute(
            Product.__table__.insert(),
            products
        )
        await db.commit()

    @staticmethod
    async def paginated_query(
        db: Session,
        model,
        page: int = 1,
        size: int = 20,
        filters: Optional[List] = None
    ):
        """Efficient pagination"""
        query = select(model)

        if filters:
            query = query.where(and_(*filters))

        # Use offset and limit for pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # Get total count in same query using window function
        count_query = select(func.count()).select_from(model)
        if filters:
            count_query = count_query.where(and_(*filters))

        total = await db.scalar(count_query)
        items = await db.execute(query)

        return {
            "items": items.scalars().all(),
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
```

## Summary

This comprehensive API development guide demonstrates:

1. **Basic APIs**: Hello World and simple endpoints
2. **CRUD Operations**: Complete RESTful API with database
3. **Microservices**: Service architecture and communication
4. **GraphQL**: Schema, resolvers, and subscriptions
5. **WebSockets**: Real-time communication
6. **Full Stack**: Complete application with frontend
7. **Security**: Authentication, authorization, rate limiting
8. **Performance**: Caching, optimization, and scaling

Each example provides:
- Working code implementations
- Testing strategies
- Best practices
- Performance considerations
- Security implementations

Use these examples as templates for building production-ready APIs with the Claude Code Context Engineering system.
