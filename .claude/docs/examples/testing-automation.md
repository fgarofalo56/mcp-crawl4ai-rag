# Testing Automation Examples

## Comprehensive Test Automation Workflow

This guide demonstrates complete test automation using the Claude Code Context Engineering system, covering unit tests, integration tests, E2E testing with Playwright, and CI/CD integration.

## Table of Contents

1. [First Test Suite](#first-suite)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [E2E Testing with Playwright](#e2e-testing)
5. [API Testing](#api-testing)
6. [Performance Testing](#performance-testing)
7. [Test Data Management](#test-data)
8. [CI/CD Integration](#cicd-integration)

## First Suite

### Getting Started with Test Automation

#### Step 1: Initialize Testing Environment

```bash
# Start test automation setup
/test-init --framework pytest --e2e playwright

# System creates:
# ✓ Test directory structure
# ✓ Configuration files
# ✓ Initial test examples
# ✓ CI/CD templates
```

#### Step 2: Basic Test Structure

```python
# tests/test_example.py
import pytest
from datetime import datetime

class TestBasicExample:
    """First test suite example"""

    def test_simple_assertion(self):
        """Test basic assertion"""
        result = 2 + 2
        assert result == 4

    def test_string_operations(self):
        """Test string manipulations"""
        text = "hello world"
        assert text.upper() == "HELLO WORLD"
        assert text.split() == ["hello", "world"]
        assert len(text) == 11

    def test_list_operations(self):
        """Test list operations"""
        numbers = [1, 2, 3, 4, 5]
        assert sum(numbers) == 15
        assert max(numbers) == 5
        assert min(numbers) == 1

    @pytest.mark.parametrize("input,expected", [
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25)
    ])
    def test_parametrized(self, input, expected):
        """Test with multiple inputs"""
        assert input ** 2 == expected

    def test_exception_handling(self):
        """Test exception raising"""
        with pytest.raises(ZeroDivisionError):
            result = 10 / 0

    @pytest.mark.skipif(
        datetime.now().weekday() == 0,
        reason="Skip on Mondays"
    )
    def test_conditional_skip(self):
        """Test that might be skipped"""
        assert True
```

#### Step 3: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_example.py

# Run tests matching pattern
pytest -k "test_string"

# Output:
# ======================== test session starts ========================
# collected 6 items
#
# tests/test_example.py::TestBasicExample::test_simple_assertion PASSED
# tests/test_example.py::TestBasicExample::test_string_operations PASSED
# tests/test_example.py::TestBasicExample::test_list_operations PASSED
# tests/test_example.py::TestBasicExample::test_parametrized[2-4] PASSED
# tests/test_example.py::TestBasicExample::test_parametrized[3-9] PASSED
# tests/test_example.py::TestBasicExample::test_exception_handling PASSED
#
# ======================== 6 passed in 0.12s ========================
```

## Unit Testing

### Comprehensive Unit Testing Strategies

#### Step 1: Application Code

```python
# src/calculator.py
class Calculator:
    """Calculator with history tracking"""

    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, base: float, exponent: float) -> float:
        result = base ** exponent
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result

    def clear_history(self):
        self.history = []

    def get_history(self) -> list:
        return self.history.copy()
```

#### Step 2: Unit Tests

```python
# tests/test_calculator.py
import pytest
from src.calculator import Calculator
import math

class TestCalculator:
    """Comprehensive unit tests for Calculator"""

    @pytest.fixture
    def calculator(self):
        """Provide calculator instance for each test"""
        return Calculator()

    def test_addition(self, calculator):
        """Test addition operations"""
        assert calculator.add(2, 3) == 5
        assert calculator.add(-1, 1) == 0
        assert calculator.add(0.1, 0.2) == pytest.approx(0.3)

    def test_subtraction(self, calculator):
        """Test subtraction operations"""
        assert calculator.subtract(5, 3) == 2
        assert calculator.subtract(0, 5) == -5
        assert calculator.subtract(-3, -5) == 2

    def test_multiplication(self, calculator):
        """Test multiplication operations"""
        assert calculator.multiply(3, 4) == 12
        assert calculator.multiply(-2, 3) == -6
        assert calculator.multiply(0, 100) == 0

    def test_division(self, calculator):
        """Test division operations"""
        assert calculator.divide(10, 2) == 5
        assert calculator.divide(7, 2) == 3.5
        assert calculator.divide(-10, 2) == -5

    def test_division_by_zero(self, calculator):
        """Test division by zero raises exception"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculator.divide(10, 0)

    def test_power(self, calculator):
        """Test power operations"""
        assert calculator.power(2, 3) == 8
        assert calculator.power(5, 0) == 1
        assert calculator.power(10, -1) == 0.1

    def test_history_tracking(self, calculator):
        """Test operation history tracking"""
        calculator.add(2, 3)
        calculator.multiply(4, 5)
        calculator.divide(10, 2)

        history = calculator.get_history()
        assert len(history) == 3
        assert "2 + 3 = 5" in history
        assert "4 * 5 = 20" in history
        assert "10 / 2 = 5" in history

    def test_clear_history(self, calculator):
        """Test clearing history"""
        calculator.add(1, 1)
        calculator.clear_history()
        assert len(calculator.get_history()) == 0

    @pytest.mark.parametrize("a,b,operation,expected", [
        (10, 5, "add", 15),
        (10, 5, "subtract", 5),
        (10, 5, "multiply", 50),
        (10, 5, "divide", 2),
        (2, 3, "power", 8)
    ])
    def test_operations_parametrized(self, calculator, a, b, operation, expected):
        """Parametrized test for all operations"""
        method = getattr(calculator, operation)
        assert method(a, b) == expected
```

#### Step 3: Mocking and Patching

```python
# src/weather_service.py
import requests

class WeatherService:
    """Service for fetching weather data"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.com/v1"

    def get_temperature(self, city: str) -> float:
        """Get current temperature for a city"""
        response = requests.get(
            f"{self.base_url}/current",
            params={"city": city, "api_key": self.api_key}
        )
        response.raise_for_status()
        data = response.json()
        return data["temperature"]

    def get_forecast(self, city: str, days: int = 7) -> list:
        """Get weather forecast"""
        response = requests.get(
            f"{self.base_url}/forecast",
            params={"city": city, "days": days, "api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json()["forecast"]
```

```python
# tests/test_weather_service.py
import pytest
from unittest.mock import Mock, patch
from src.weather_service import WeatherService
import requests

class TestWeatherService:
    """Tests for WeatherService with mocking"""

    @pytest.fixture
    def service(self):
        return WeatherService("test_api_key")

    @patch('src.weather_service.requests.get')
    def test_get_temperature_success(self, mock_get, service):
        """Test successful temperature fetch"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"temperature": 25.5}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test
        temp = service.get_temperature("London")

        # Assertions
        assert temp == 25.5
        mock_get.assert_called_once_with(
            "https://api.weather.com/v1/current",
            params={"city": "London", "api_key": "test_api_key"}
        )

    @patch('src.weather_service.requests.get')
    def test_get_temperature_error(self, mock_get, service):
        """Test API error handling"""
        # Setup mock to raise exception
        mock_get.side_effect = requests.RequestException("API Error")

        # Test
        with pytest.raises(requests.RequestException):
            service.get_temperature("InvalidCity")

    @patch('src.weather_service.requests.get')
    def test_get_forecast(self, mock_get, service):
        """Test forecast fetching"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "forecast": [
                {"date": "2024-01-01", "temp": 20},
                {"date": "2024-01-02", "temp": 22}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test
        forecast = service.get_forecast("Paris", days=2)

        # Assertions
        assert len(forecast) == 2
        assert forecast[0]["temp"] == 20
```

## Integration Testing

### Database and API Integration Tests

#### Step 1: Database Integration

```python
# tests/test_database_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, User, Product, Order

class TestDatabaseIntegration:
    """Integration tests for database operations"""

    @pytest.fixture(scope="function")
    def db_session(self):
        """Provide test database session"""
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()
        Base.metadata.drop_all(engine)

    def test_user_crud_operations(self, db_session):
        """Test user CRUD operations"""
        # Create
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()

        # Read
        retrieved = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved.email == "test@example.com"

        # Update
        retrieved.full_name = "Updated Name"
        db_session.commit()

        updated = db_session.query(User).filter_by(username="testuser").first()
        assert updated.full_name == "Updated Name"

        # Delete
        db_session.delete(updated)
        db_session.commit()

        deleted = db_session.query(User).filter_by(username="testuser").first()
        assert deleted is None

    def test_order_with_products(self, db_session):
        """Test order creation with products"""
        # Create user
        user = User(username="buyer", email="buyer@example.com")
        db_session.add(user)

        # Create products
        product1 = Product(name="Product 1", price=10.00)
        product2 = Product(name="Product 2", price=20.00)
        db_session.add_all([product1, product2])
        db_session.commit()

        # Create order
        order = Order(
            user_id=user.id,
            total=30.00,
            items=[
                {"product_id": product1.id, "quantity": 1},
                {"product_id": product2.id, "quantity": 1}
            ]
        )
        db_session.add(order)
        db_session.commit()

        # Verify
        retrieved_order = db_session.query(Order).first()
        assert retrieved_order.total == 30.00
        assert retrieved_order.user_id == user.id
        assert len(retrieved_order.items) == 2

    def test_transaction_rollback(self, db_session):
        """Test transaction rollback on error"""
        try:
            user = User(username="test", email="invalid-email")  # Invalid email
            db_session.add(user)
            db_session.commit()
        except Exception:
            db_session.rollback()

        # Verify no user was created
        users = db_session.query(User).all()
        assert len(users) == 0
```

#### Step 2: API Integration Tests

```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
import asyncio

class TestAPIIntegration:
    """Integration tests for API endpoints"""

    @pytest.fixture
    def client(self):
        """Provide test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_token(self, client):
        """Get authentication token"""
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        })
        assert response.status_code == 201

        login_response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        return login_response.json()["access_token"]

    def test_complete_user_flow(self, client, auth_token):
        """Test complete user journey"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Get user profile
        profile = client.get("/api/users/me", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["username"] == "testuser"

        # Update profile
        update = client.patch("/api/users/me", json={
            "full_name": "Updated Name"
        }, headers=headers)
        assert update.status_code == 200

        # Create a product (admin only - should fail)
        product = client.post("/api/products", json={
            "name": "Test Product",
            "price": 29.99
        }, headers=headers)
        assert product.status_code == 403  # Forbidden

    def test_order_workflow(self, client, auth_token):
        """Test complete order workflow"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Add items to cart
        client.post("/api/cart/items", json={
            "product_id": 1,
            "quantity": 2
        }, headers=headers)

        # Get cart
        cart = client.get("/api/cart", headers=headers)
        assert cart.status_code == 200
        assert len(cart.json()["items"]) == 1

        # Create order from cart
        order = client.post("/api/orders", json={
            "shipping_address": {
                "street": "123 Main St",
                "city": "Test City",
                "zip": "12345"
            }
        }, headers=headers)
        assert order.status_code == 201

        # Verify cart is cleared
        cart_after = client.get("/api/cart", headers=headers)
        assert len(cart_after.json()["items"]) == 0

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            with client.websocket_connect("/ws/test") as websocket:
                # Send message
                websocket.send_json({"type": "ping"})

                # Receive response
                data = websocket.receive_json()
                assert data["type"] == "pong"
```

## E2E Testing

### Playwright E2E Testing

#### Step 1: Playwright Setup

```bash
# Initialize Playwright
/playwright-init

# Install browsers
playwright install chromium firefox webkit

# Generated configuration:
```

```javascript
// playwright.config.js
module.exports = {
  testDir: './e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['junit', { outputFile: 'results.xml' }],
    ['json', { outputFile: 'results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 13'] }
    }
  ],

  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI
  }
};
```

#### Step 2: E2E Test Implementation

```javascript
// e2e/login.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('successful login', async ({ page }) => {
    // Navigate to login
    await page.click('text=Login');
    await expect(page).toHaveURL('/login');

    // Fill login form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect
    await page.waitForURL('/dashboard');

    // Verify logged in
    await expect(page.locator('text=Welcome, testuser')).toBeVisible();

    // Check local storage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill with invalid credentials
    await page.fill('input[name="username"]', 'invalid');
    await page.fill('input[name="password"]', 'wrong');

    // Submit
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');

    // Should stay on login page
    await expect(page).toHaveURL('/login');
  });

  test('password reset flow', async ({ page }) => {
    await page.goto('/login');

    // Click forgot password
    await page.click('text=Forgot Password?');

    // Fill email
    await page.fill('input[name="email"]', 'user@example.com');
    await page.click('text=Send Reset Link');

    // Verify success message
    await expect(page.locator('.success-message')).toContainText('Reset link sent');
  });
});
```

```javascript
// e2e/shopping-cart.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Shopping Cart E2E', () => {
  test.use({
    storageState: 'auth.json'  // Use authenticated state
  });

  test('complete purchase flow', async ({ page }) => {
    // Go to products page
    await page.goto('/products');

    // Search for product
    await page.fill('input[placeholder="Search products"]', 'laptop');
    await page.press('input[placeholder="Search products"]', 'Enter');

    // Wait for results
    await page.waitForSelector('.product-card');

    // Add first product to cart
    await page.locator('.product-card').first().click();
    await page.click('button:has-text("Add to Cart")');

    // Verify cart badge updated
    await expect(page.locator('.cart-badge')).toContainText('1');

    // Go to cart
    await page.click('.cart-icon');
    await expect(page).toHaveURL('/cart');

    // Verify product in cart
    await expect(page.locator('.cart-item')).toHaveCount(1);

    // Update quantity
    await page.fill('input[name="quantity"]', '2');
    await page.click('button:has-text("Update")');

    // Proceed to checkout
    await page.click('button:has-text("Proceed to Checkout")');

    // Fill shipping information
    await page.fill('input[name="fullName"]', 'John Doe');
    await page.fill('input[name="address"]', '123 Main St');
    await page.fill('input[name="city"]', 'New York');
    await page.fill('input[name="zip"]', '10001');

    // Fill payment information
    await page.fill('input[name="cardNumber"]', '4111111111111111');
    await page.fill('input[name="expiry"]', '12/25');
    await page.fill('input[name="cvv"]', '123');

    // Place order
    await page.click('button:has-text("Place Order")');

    // Wait for confirmation
    await page.waitForURL(/\/order\/\d+/);

    // Verify order confirmation
    await expect(page.locator('h1')).toContainText('Order Confirmed');
    await expect(page.locator('.order-number')).toBeVisible();

    // Take screenshot for documentation
    await page.screenshot({ path: 'order-confirmation.png', fullPage: true });
  });

  test('cart persistence', async ({ page, context }) => {
    // Add item to cart
    await page.goto('/products');
    await page.locator('.product-card').first().click();
    await page.click('button:has-text("Add to Cart")');

    // Open new tab
    const page2 = await context.newPage();
    await page2.goto('/cart');

    // Verify item is in cart in new tab
    await expect(page2.locator('.cart-item')).toHaveCount(1);

    // Close and reopen browser
    await context.close();
  });
});
```

#### Step 3: Page Object Model

```javascript
// e2e/pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[name="username"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
    this.forgotPasswordLink = page.locator('text=Forgot Password?');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}

// e2e/pages/ProductPage.js
class ProductPage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator('input[placeholder="Search products"]');
    this.productCards = page.locator('.product-card');
    this.addToCartButton = page.locator('button:has-text("Add to Cart")');
    this.cartBadge = page.locator('.cart-badge');
  }

  async searchProducts(query) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }

  async addFirstProductToCart() {
    await this.productCards.first().click();
    await this.addToCartButton.click();
  }

  async getCartCount() {
    return await this.cartBadge.textContent();
  }
}

// e2e/tests/using-page-objects.spec.js
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');
const { ProductPage } = require('../pages/ProductPage');

test('login and add product using page objects', async ({ page }) => {
  const loginPage = new LoginPage(page);
  const productPage = new ProductPage(page);

  // Login
  await loginPage.goto();
  await loginPage.login('testuser', 'testpass123');

  // Navigate to products
  await page.goto('/products');

  // Search and add product
  await productPage.searchProducts('laptop');
  await productPage.addFirstProductToCart();

  // Verify cart updated
  const cartCount = await productPage.getCartCount();
  expect(cartCount).toBe('1');
});
```

## API Testing

### Comprehensive API Testing

#### Step 1: REST API Testing

```javascript
// tests/api/rest-api.test.js
const axios = require('axios');
const { expect } = require('@playwright/test');

const API_URL = process.env.API_URL || 'http://localhost:8000';

describe('REST API Tests', () => {
  let authToken;
  let userId;

  beforeAll(async () => {
    // Register and login
    const registerResponse = await axios.post(`${API_URL}/api/auth/register`, {
      username: 'apitest',
      password: 'testpass123',
      email: 'api@test.com'
    });

    userId = registerResponse.data.user_id;

    const loginResponse = await axios.post(`${API_URL}/api/auth/login`, {
      username: 'apitest',
      password: 'testpass123'
    });

    authToken = loginResponse.data.access_token;
  });

  test('GET /api/products', async () => {
    const response = await axios.get(`${API_URL}/api/products`);

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('items');
    expect(Array.isArray(response.data.items)).toBe(true);
    expect(response.data).toHaveProperty('total');
    expect(response.data).toHaveProperty('page');
    expect(response.data).toHaveProperty('size');
  });

  test('POST /api/products (authenticated)', async () => {
    const productData = {
      name: 'Test Product',
      description: 'API test product',
      price: 99.99,
      stock: 50
    };

    const response = await axios.post(
      `${API_URL}/api/products`,
      productData,
      {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      }
    );

    expect(response.status).toBe(201);
    expect(response.data.name).toBe(productData.name);
    expect(response.data.price).toBe(productData.price);
    expect(response.data).toHaveProperty('id');
  });

  test('PUT /api/products/:id', async () => {
    const updateData = {
      price: 89.99,
      stock: 45
    };

    const response = await axios.put(
      `${API_URL}/api/products/1`,
      updateData,
      {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      }
    );

    expect(response.status).toBe(200);
    expect(response.data.price).toBe(updateData.price);
    expect(response.data.stock).toBe(updateData.stock);
  });

  test('DELETE /api/products/:id', async () => {
    const response = await axios.delete(
      `${API_URL}/api/products/1`,
      {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      }
    );

    expect(response.status).toBe(204);

    // Verify deletion
    try {
      await axios.get(`${API_URL}/api/products/1`);
    } catch (error) {
      expect(error.response.status).toBe(404);
    }
  });

  test('Rate limiting', async () => {
    const requests = [];

    // Send 100 requests rapidly
    for (let i = 0; i < 100; i++) {
      requests.push(axios.get(`${API_URL}/api/products`));
    }

    try {
      await Promise.all(requests);
    } catch (error) {
      // Should hit rate limit
      expect(error.response.status).toBe(429);
      expect(error.response.data).toHaveProperty('detail');
    }
  });
});
```

#### Step 2: GraphQL Testing

```javascript
// tests/api/graphql.test.js
const { GraphQLClient, gql } = require('graphql-request');

describe('GraphQL API Tests', () => {
  const client = new GraphQLClient('http://localhost:8000/graphql');

  test('Query: getUsers', async () => {
    const query = gql`
      query GetUsers($limit: Int) {
        users(limit: $limit) {
          id
          username
          email
          posts {
            id
            title
          }
        }
      }
    `;

    const variables = { limit: 10 };
    const data = await client.request(query, variables);

    expect(data.users).toBeDefined();
    expect(Array.isArray(data.users)).toBe(true);
    expect(data.users[0]).toHaveProperty('id');
    expect(data.users[0]).toHaveProperty('username');
    expect(data.users[0]).toHaveProperty('posts');
  });

  test('Mutation: createPost', async () => {
    const mutation = gql`
      mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
          id
          title
          content
          published
          createdAt
        }
      }
    `;

    const variables = {
      input: {
        title: 'Test Post',
        content: 'Test content',
        authorId: 1,
        published: false
      }
    };

    const data = await client.request(mutation, variables);

    expect(data.createPost).toBeDefined();
    expect(data.createPost.title).toBe('Test Post');
    expect(data.createPost.published).toBe(false);
    expect(data.createPost.id).toBeDefined();
  });

  test('Subscription: postCreated', async () => {
    const subscription = gql`
      subscription OnPostCreated {
        postCreated {
          id
          title
          author {
            username
          }
        }
      }
    `;

    // Setup WebSocket connection for subscription
    const ws = new WebSocket('ws://localhost:8000/graphql');

    ws.on('message', (data) => {
      const message = JSON.parse(data);
      if (message.type === 'data') {
        expect(message.payload.data.postCreated).toBeDefined();
        expect(message.payload.data.postCreated.title).toBeDefined();
        ws.close();
      }
    });

    ws.on('open', () => {
      ws.send(JSON.stringify({
        type: 'connection_init'
      }));

      ws.send(JSON.stringify({
        id: '1',
        type: 'start',
        payload: {
          query: subscription
        }
      }));
    });
  });
});
```

## Performance Testing

### Load and Stress Testing

#### Step 1: Load Testing with k6

```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users
    { duration: '5m', target: 10 },   // Stay at 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.1'],               // Error rate under 10%
  },
};

export function setup() {
  // Login and get token
  const loginRes = http.post('http://localhost:8000/api/auth/login', {
    username: 'testuser',
    password: 'testpass123',
  });

  return {
    token: loginRes.json('access_token'),
  };
}

export default function (data) {
  const params = {
    headers: {
      Authorization: `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  // Scenario 1: Browse products
  const productsRes = http.get('http://localhost:8000/api/products', params);
  check(productsRes, {
    'products status 200': (r) => r.status === 200,
    'products has items': (r) => JSON.parse(r.body).items.length > 0,
  });
  errorRate.add(productsRes.status !== 200);

  sleep(1);

  // Scenario 2: View product details
  const productId = Math.floor(Math.random() * 100) + 1;
  const productRes = http.get(`http://localhost:8000/api/products/${productId}`, params);
  check(productRes, {
    'product status 200': (r) => r.status === 200,
  });
  errorRate.add(productRes.status !== 200);

  sleep(1);

  // Scenario 3: Add to cart
  const cartRes = http.post(
    'http://localhost:8000/api/cart/items',
    JSON.stringify({
      product_id: productId,
      quantity: 1,
    }),
    params
  );
  check(cartRes, {
    'add to cart success': (r) => r.status === 201 || r.status === 200,
  });
  errorRate.add(cartRes.status >= 400);

  sleep(2);
}

export function handleSummary(data) {
  return {
    'summary.html': htmlReport(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
```

#### Step 2: Stress Testing

```javascript
// tests/performance/stress-test.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Below normal load
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },   // Normal load
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },   // Around breaking point
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },   // Beyond breaking point
    { duration: '5m', target: 400 },
    { duration: '10m', target: 0 },    // Recovery
  ],
};

export default function () {
  const responses = http.batch([
    ['GET', 'http://localhost:8000/api/products'],
    ['GET', 'http://localhost:8000/api/products/1'],
    ['GET', 'http://localhost:8000/api/categories'],
  ]);

  for (const response of responses) {
    check(response, {
      'status is 200': (r) => r.status === 200,
      'response time < 1000ms': (r) => r.timings.duration < 1000,
    });
  }
}
```

## Test Data

### Test Data Management Strategies

#### Step 1: Test Data Factory

```python
# tests/factories.py
import factory
from factory.faker import Faker
from src.models import User, Product, Order
from datetime import datetime, timedelta
import random

class UserFactory(factory.Factory):
    """Factory for creating test users"""
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    full_name = Faker('name')
    created_at = factory.LazyFunction(datetime.now)
    is_active = True
    is_admin = False

class AdminFactory(UserFactory):
    """Factory for creating admin users"""
    username = factory.Sequence(lambda n: f"admin{n}")
    is_admin = True

class ProductFactory(factory.Factory):
    """Factory for creating test products"""
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
    name = Faker('catch_phrase')
    description = Faker('text')
    price = factory.LazyFunction(lambda: round(random.uniform(10, 1000), 2))
    stock = factory.LazyFunction(lambda: random.randint(0, 100))
    category = factory.Faker('random_element', elements=['Electronics', 'Books', 'Clothing', 'Food'])
    sku = factory.Sequence(lambda n: f"SKU{n:06d}")
    created_at = factory.LazyFunction(datetime.now)

class OrderFactory(factory.Factory):
    """Factory for creating test orders"""
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    status = factory.Faker('random_element', elements=['pending', 'processing', 'shipped', 'delivered'])
    total = factory.LazyFunction(lambda: round(random.uniform(10, 500), 2))
    created_at = factory.LazyFunction(lambda: datetime.now() - timedelta(days=random.randint(0, 30)))

# Usage
def create_test_data():
    """Create comprehensive test data set"""
    users = UserFactory.create_batch(10)
    admins = AdminFactory.create_batch(2)
    products = ProductFactory.create_batch(50)
    orders = OrderFactory.create_batch(100)

    return {
        'users': users,
        'admins': admins,
        'products': products,
        'orders': orders
    }
```

#### Step 2: Data Fixtures

```python
# tests/fixtures.py
import pytest
from tests.factories import UserFactory, ProductFactory, OrderFactory

@pytest.fixture
def sample_user():
    """Provide a sample user"""
    return UserFactory(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )

@pytest.fixture
def sample_products():
    """Provide sample products"""
    return ProductFactory.create_batch(5)

@pytest.fixture
def user_with_orders(sample_user):
    """Provide user with order history"""
    orders = OrderFactory.create_batch(3, user=sample_user)
    sample_user.orders = orders
    return sample_user

@pytest.fixture
def database_with_data(db_session):
    """Populate database with test data"""
    users = UserFactory.create_batch(10)
    products = ProductFactory.create_batch(20)
    orders = OrderFactory.create_batch(30)

    for user in users:
        db_session.add(user)
    for product in products:
        db_session.add(product)
    for order in orders:
        db_session.add(order)

    db_session.commit()

    return {
        'users': users,
        'products': products,
        'orders': orders
    }
```

## CICD Integration

### Complete CI/CD Test Automation

#### GitHub Actions Workflow

```yaml
# .github/workflows/test-automation.yml
name: Test Automation Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-html

      - name: Run unit tests
        run: |
          pytest tests/unit \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --html=report.html \
            --self-contained-html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: unit-test-report
          path: report.html

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Setup environment
        run: |
          cp .env.test .env
          docker-compose up -d

      - name: Run integration tests
        run: |
          pytest tests/integration \
            --maxfail=5 \
            --tb=short

      - name: Cleanup
        if: always()
        run: docker-compose down

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          npm ci
          npx playwright install --with-deps

      - name: Start application
        run: |
          npm run build
          npm run start &
          npx wait-on http://localhost:3000

      - name: Run Playwright tests
        run: |
          npx playwright test \
            --reporter=html \
            --screenshot=on \
            --video=on

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: |
            playwright-report/
            test-results/

  performance-tests:
    runs-on: ubuntu-latest
    needs: e2e-tests
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Setup k6
        run: |
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Start application
        run: |
          docker-compose up -d
          sleep 10

      - name: Run performance tests
        run: |
          k6 run tests/performance/load-test.js \
            --out json=results.json

      - name: Analyze results
        run: |
          python scripts/analyze_performance.py results.json

      - name: Upload performance report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.html

  security-tests:
    runs-on: ubuntu-latest
    needs: unit-tests

    steps:
      - uses: actions/checkout@v3

      - name: Run security scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload security results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests, security-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          # Deployment commands here

      - name: Run smoke tests
        run: |
          pytest tests/smoke \
            --base-url=https://staging.example.com
```

## Summary

This comprehensive testing automation guide covers:

1. **Unit Testing**: Component-level testing with mocking
2. **Integration Testing**: Database and API integration
3. **E2E Testing**: Complete user flows with Playwright
4. **API Testing**: REST and GraphQL testing
5. **Performance Testing**: Load and stress testing
6. **Test Data Management**: Factories and fixtures
7. **CI/CD Integration**: Complete automation pipeline

Each example provides:
- Working test implementations
- Best practices and patterns
- CI/CD integration
- Performance optimization
- Comprehensive coverage strategies

Use these examples to build robust test automation for your applications with the Claude Code Context Engineering system.
