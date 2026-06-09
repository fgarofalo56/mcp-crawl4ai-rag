# Code Quality

Comprehensive guidelines for maintaining high code quality with Claude Code.

## Overview

This guide covers code review practices, testing strategies, documentation standards, security practices, performance guidelines, and Azure-specific best practices.

## Code Review Guidelines

### Self-Review Checklist

Before creating a pull request, review your own code:

**Functionality**
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling in place
- [ ] No hardcoded values
- [ ] Configuration externalized

**Code Quality**
- [ ] Follows team style guide
- [ ] No code duplication
- [ ] Functions are focused and small
- [ ] Clear variable/function names
- [ ] No commented-out code
- [ ] No debug statements

**Testing**
- [ ] Unit tests added
- [ ] Integration tests added (if applicable)
- [ ] Tests pass locally
- [ ] Coverage meets threshold
- [ ] Edge cases tested

**Documentation**
- [ ] Code comments where needed
- [ ] API documentation updated
- [ ] README updated (if applicable)
- [ ] Breaking changes documented

**Security**
- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Authentication/authorization checked

**Performance**
- [ ] No obvious performance issues
- [ ] Database queries optimized
- [ ] Caching considered
- [ ] Resource cleanup (connections, files)

### Using Claude for Self-Review

```bash
# Comprehensive review
"Review my changes for code quality, security, and performance:

[git diff output or file names]

Check for:
1. Code smells and anti-patterns
2. Security vulnerabilities
3. Performance issues
4. Missing error handling
5. Insufficient tests
6. Documentation gaps"
```

### Review Response Pattern

**Address all feedback:**
```bash
# For each issue found
"Fix [specific issue]"

# Verify fix
npm test

# Document why if not fixing
# "Not fixing [issue] because [reason]"
```

### Automated Review Tools

**Configure pre-commit checks:**
```json
{
  "hooks": {
    "preCommit": [
      "npm run lint",
      "npm run type-check",
      "npm test",
      "npm run security-scan"
    ]
  }
}
```

**Quality gates:**
```json
{
  "qualityGates": {
    "codeQualityScore": 8,
    "testCoverageThreshold": 80,
    "securityScan": true,
    "lintCommand": "npm run lint"
  }
}
```

## Testing Strategies

### Test Pyramid

**Structure your tests:**
```
        /\
       /  \  E2E Tests (10%)
      /____\
     /      \ Integration Tests (20%)
    /________\
   /          \ Unit Tests (70%)
  /__________\
```

### Unit Testing

**Pattern: Test individual functions**
```typescript
// Function to test
function calculateDiscount(price: number, discountPercent: number): number {
  if (price < 0 || discountPercent < 0 || discountPercent > 100) {
    throw new Error('Invalid input');
  }
  return price * (1 - discountPercent / 100);
}

// Tests
describe('calculateDiscount', () => {
  it('should calculate discount correctly', () => {
    expect(calculateDiscount(100, 10)).toBe(90);
  });

  it('should handle zero discount', () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it('should handle 100% discount', () => {
    expect(calculateDiscount(100, 100)).toBe(0);
  });

  it('should throw error for negative price', () => {
    expect(() => calculateDiscount(-100, 10)).toThrow('Invalid input');
  });

  it('should throw error for negative discount', () => {
    expect(() => calculateDiscount(100, -10)).toThrow('Invalid input');
  });

  it('should throw error for discount > 100', () => {
    expect(() => calculateDiscount(100, 150)).toThrow('Invalid input');
  });
});
```

**Request tests from Claude:**
```bash
"Add comprehensive unit tests for the calculateDiscount function including edge cases"
```

### Integration Testing

**Pattern: Test component interactions**
```typescript
// Integration test for API endpoint
describe('POST /api/users', () => {
  let app: Express;
  let database: Database;

  beforeEach(async () => {
    app = createApp();
    database = await createTestDatabase();
  });

  afterEach(async () => {
    await database.cleanup();
  });

  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'test@example.com',
        name: 'Test User',
        password: 'SecurePass123!'
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.email).toBe('test@example.com');

    // Verify in database
    const user = await database.users.findById(response.body.id);
    expect(user).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });

  it('should return 400 for invalid email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'invalid-email',
        name: 'Test User',
        password: 'SecurePass123!'
      });

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });
});
```

### End-to-End Testing

**Pattern: Test complete user flows**
```typescript
// E2E test with Playwright
test('user can complete checkout', async ({ page }) => {
  // Navigate to product
  await page.goto('/products/laptop');

  // Add to cart
  await page.click('button:has-text("Add to Cart")');

  // Go to cart
  await page.click('a:has-text("Cart")');

  // Verify item in cart
  await expect(page.locator('.cart-item')).toContainText('Laptop');

  // Proceed to checkout
  await page.click('button:has-text("Checkout")');

  // Fill shipping info
  await page.fill('input[name="address"]', '123 Main St');
  await page.fill('input[name="city"]', 'Boston');
  await page.fill('input[name="zipCode"]', '02101');

  // Fill payment info
  await page.fill('input[name="cardNumber"]', '4242424242424242');
  await page.fill('input[name="expiry"]', '12/25');
  await page.fill('input[name="cvv"]', '123');

  // Submit order
  await page.click('button:has-text("Place Order")');

  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.order-number')).toBeVisible();
});
```

**Request E2E tests from Claude:**
```bash
"Create an E2E test for the complete user registration and login flow using Playwright"
```

### Test Coverage Goals

**Coverage thresholds by code type:**
```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "coverageByType": {
      "business-logic": 95,
      "api-routes": 90,
      "utilities": 85,
      "ui-components": 75,
      "config": 50
    }
  }
}
```

### Testing Best Practices

**1. Arrange-Act-Assert (AAA) Pattern**
```typescript
test('should update user profile', async () => {
  // Arrange
  const user = await createTestUser();
  const updates = { name: 'New Name' };

  // Act
  const result = await userService.updateProfile(user.id, updates);

  // Assert
  expect(result.name).toBe('New Name');
});
```

**2. Test Independence**
```typescript
// Bad: Tests depend on order
test('create user', () => { /* creates user */ });
test('get user', () => { /* assumes user exists */ });

// Good: Each test is independent
test('create user', async () => {
  const user = await createUser();
  expect(user).toBeDefined();
});

test('get user', async () => {
  const user = await createUser(); // Create own test data
  const found = await getUser(user.id);
  expect(found).toBeDefined();
});
```

**3. Use Test Fixtures**
```typescript
// fixtures/users.ts
export const testUsers = {
  valid: {
    email: 'test@example.com',
    name: 'Test User',
    password: 'SecurePass123!'
  },
  admin: {
    email: 'admin@example.com',
    name: 'Admin User',
    password: 'AdminPass123!',
    role: 'admin'
  }
};

// In tests
import { testUsers } from './fixtures/users';

test('create user', async () => {
  const user = await createUser(testUsers.valid);
  expect(user.email).toBe(testUsers.valid.email);
});
```

**4. Mock External Dependencies**
```typescript
// Mock external API
jest.mock('./paymentService', () => ({
  processPayment: jest.fn().mockResolvedValue({
    success: true,
    transactionId: 'txn_123'
  })
}));

test('checkout creates order', async () => {
  const order = await checkoutService.processOrder(cart);

  expect(order.status).toBe('completed');
  expect(paymentService.processPayment).toHaveBeenCalledWith(
    expect.objectContaining({
      amount: 100
    })
  );
});
```

## Documentation Standards

### Code Comments

**When to comment:**
```typescript
// Good: Explain WHY, not WHAT
// Use exponential backoff to handle rate limiting from external API
async function retryWithBackoff(fn, maxRetries = 3) {
  // Implementation...
}

// Bad: Redundant comment
// Increment counter by 1
counter++;

// Good: Document complex logic
// Calculate discount tier based on cumulative purchase amount
// Tier 1: $0-999 = 5%
// Tier 2: $1000-4999 = 10%
// Tier 3: $5000+ = 15%
function calculateDiscountTier(totalPurchases) {
  // Implementation...
}
```

**Function documentation:**
```typescript
/**
 * Processes a payment using the configured payment provider
 *
 * @param orderId - The unique order identifier
 * @param amount - Payment amount in cents
 * @param paymentMethod - Payment method details
 * @returns Promise resolving to payment result
 * @throws PaymentError if payment processing fails
 *
 * @example
 * ```typescript
 * const result = await processPayment('ord_123', 5000, {
 *   type: 'card',
 *   token: 'tok_visa'
 * });
 * ```
 */
async function processPayment(
  orderId: string,
  amount: number,
  paymentMethod: PaymentMethod
): Promise<PaymentResult> {
  // Implementation...
}
```

### API Documentation

**Document all public APIs:**
```typescript
/**
 * User Management API
 *
 * @module UserAPI
 */

/**
 * GET /api/users/:id
 *
 * Retrieves a user by ID
 *
 * @route GET /api/users/:id
 * @param {string} id.path.required - User ID
 * @returns {User} 200 - User object
 * @returns {Error} 404 - User not found
 * @returns {Error} 500 - Internal server error
 *
 * @example
 * GET /api/users/user_123
 * Response: {
 *   "id": "user_123",
 *   "email": "user@example.com",
 *   "name": "John Doe"
 * }
 */
router.get('/users/:id', async (req, res) => {
  // Implementation...
});
```

**OpenAPI/Swagger:**
```yaml
paths:
  /api/users/{id}:
    get:
      summary: Get user by ID
      description: Retrieves a user's information by their unique identifier
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
          description: User ID
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
        '500':
          description: Internal server error
```

### README Documentation

**Essential sections:**
```markdown
# Project Name

Brief description of what this project does.

## Prerequisites

- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Installation

\`\`\`bash
npm install
cp .env.example .env
# Edit .env with your configuration
npm run db:migrate
\`\`\`

## Usage

\`\`\`bash
# Development
npm run dev

# Production
npm run build
npm start
\`\`\`

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| REDIS_URL | Redis connection string | localhost:6379 |
| JWT_SECRET | JWT signing secret | - |

## API Documentation

See [API.md](./docs/API.md) or visit `/api/docs` when running.

## Testing

\`\`\`bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage
npm test -- --coverage
\`\`\`

## Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT
```

### Architecture Documentation

**Document key decisions:**
```markdown
# Architecture Decision Record (ADR)

## ADR-001: Use PostgreSQL for Primary Database

### Status
Accepted

### Context
We need a database for storing user data, orders, and product information.

### Decision
Use PostgreSQL as the primary database.

### Consequences

**Positive:**
- ACID compliance
- Strong JSON support
- Rich query capabilities
- Excellent performance
- Wide tooling support

**Negative:**
- Requires dedicated hosting
- Scaling complexity vs. managed NoSQL

### Alternatives Considered
- MongoDB: Easier scaling but weaker consistency
- MySQL: Similar to PostgreSQL but weaker JSON support
```

## Security Practices

### Input Validation

**Always validate user input:**
```typescript
import { z } from 'zod';

// Define validation schema
const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  age: z.number().int().positive().max(150),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
});

// Validate input
function createUser(data: unknown) {
  const validated = userSchema.parse(data); // Throws if invalid
  // Use validated data
}
```

### Authentication & Authorization

**Secure password handling:**
```typescript
import bcrypt from 'bcrypt';

// Hash password
async function hashPassword(password: string): Promise<string> {
  const saltRounds = 10;
  return bcrypt.hash(password, saltRounds);
}

// Verify password
async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// Never store plain text passwords
async function createUser(email: string, password: string) {
  const user = await db.users.create({
    email,
    passwordHash: await hashPassword(password) // Store hash, not password
  });
  return user;
}
```

**JWT best practices:**
```typescript
import jwt from 'jsonwebtoken';

// Create token with expiration
function createAuthToken(userId: string): string {
  return jwt.sign(
    { userId },
    process.env.JWT_SECRET!,
    { expiresIn: '1h' } // Short expiration
  );
}

// Verify token
function verifyAuthToken(token: string): { userId: string } {
  try {
    return jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
  } catch (error) {
    throw new Error('Invalid token');
  }
}
```

### SQL Injection Prevention

**Use parameterized queries:**
```typescript
// Bad: SQL injection vulnerability
async function getUser(email: string) {
  return db.query(`SELECT * FROM users WHERE email = '${email}'`);
}

// Good: Parameterized query
async function getUser(email: string) {
  return db.query('SELECT * FROM users WHERE email = $1', [email]);
}

// Best: Use ORM
async function getUser(email: string) {
  return db.users.findOne({ where: { email } });
}
```

### XSS Prevention

**Sanitize output:**
```typescript
import DOMPurify from 'dompurify';

// Sanitize user-generated content
function renderUserContent(html: string): string {
  return DOMPurify.sanitize(html);
}

// Use React (auto-escapes)
function UserComment({ comment }: { comment: string }) {
  return <div>{comment}</div>; // React escapes by default
}

// If you must use dangerouslySetInnerHTML
function UserComment({ comment }: { comment: string }) {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: DOMPurify.sanitize(comment)
      }}
    />
  );
}
```

### Secrets Management

**Never commit secrets:**
```bash
# .env (gitignored)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=super-secret-key-change-in-production
API_KEY=sk_live_xxx

# .env.example (committed)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=change-this-in-production
API_KEY=your-api-key-here
```

**Use environment variables:**
```typescript
// config.ts
export const config = {
  database: {
    url: process.env.DATABASE_URL!
  },
  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: '1h'
  },
  api: {
    key: process.env.API_KEY!
  }
};

// Validate on startup
Object.entries(config).forEach(([key, value]) => {
  if (typeof value === 'object') {
    Object.entries(value).forEach(([subKey, subValue]) => {
      if (!subValue) {
        throw new Error(`Missing required config: ${key}.${subKey}`);
      }
    });
  }
});
```

## Performance Guidelines

### Database Optimization

**Index frequently queried fields:**
```sql
-- Add index for user lookups by email
CREATE INDEX idx_users_email ON users(email);

-- Composite index for common queries
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index for active users
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

**Optimize queries:**
```typescript
// Bad: N+1 query problem
async function getUsersWithPosts() {
  const users = await db.users.findAll();
  for (const user of users) {
    user.posts = await db.posts.findAll({ where: { userId: user.id } });
  }
  return users;
}

// Good: Single query with join
async function getUsersWithPosts() {
  return db.users.findAll({
    include: [{ model: db.posts }]
  });
}
```

### Caching

**Implement caching:**
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

async function getUser(id: string) {
  // Check cache
  const cached = await redis.get(`user:${id}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // Query database
  const user = await db.users.findById(id);

  // Store in cache (1 hour)
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));

  return user;
}

// Invalidate cache on update
async function updateUser(id: string, updates: Partial<User>) {
  const user = await db.users.update(id, updates);

  // Invalidate cache
  await redis.del(`user:${id}`);

  return user;
}
```

### API Performance

**Implement pagination:**
```typescript
interface PaginationParams {
  page: number;
  limit: number;
}

async function getUsers({ page = 1, limit = 20 }: PaginationParams) {
  const offset = (page - 1) * limit;

  const [users, total] = await Promise.all([
    db.users.findAll({ offset, limit }),
    db.users.count()
  ]);

  return {
    data: users,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit)
    }
  };
}
```

**Rate limiting:**
```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Max 100 requests per window
  message: 'Too many requests, please try again later'
});

app.use('/api/', limiter);
```

## Azure Best Practices

### Azure Functions

**Optimize cold starts:**
```typescript
// Use dependency injection for shared resources
let dbConnection: Connection;

async function getConnection() {
  if (!dbConnection) {
    dbConnection = await createConnection();
  }
  return dbConnection;
}

export async function httpTrigger(context: Context, req: HttpRequest) {
  const db = await getConnection(); // Reuse connection
  // Handle request
}
```

**Handle timeouts:**
```json
{
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    }
  }
}
```

### Azure Storage

**Optimize blob access:**
```typescript
// Use SAS tokens for temporary access
const sasToken = generateSasToken(blobName, {
  permissions: 'r',
  expiresIn: '1h'
});

// Enable CDN for static content
const cdnUrl = `https://cdn.example.com/${blobName}`;
```

### Azure Monitoring

**Application Insights:**
```typescript
import { TelemetryClient } from 'applicationinsights';

const client = new TelemetryClient(process.env.APPINSIGHTS_KEY);

// Track custom events
client.trackEvent({ name: 'UserCreated', properties: { userId } });

// Track dependencies
client.trackDependency({
  target: 'database',
  name: 'getUserById',
  data: query,
  duration: elapsed,
  success: true
});
```

## Next Steps

- [Context Management](./context-management.md) - Optimize context usage
- [Workflow Patterns](./workflow-patterns.md) - Development workflows
- [Team Collaboration](./team-collaboration.md) - Team practices
- [Quality Gates](../settings/quality-gates.md) - Automated quality checks
