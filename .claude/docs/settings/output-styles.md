# Output Styles

Configure how Claude Code responds to your requests with different verbosity and formatting levels.

## Overview

Output styles control the verbosity, formatting, and detail level of Claude Code's responses. Choose the right style for your workflow, context window management, and personal preferences.

## Available Styles

### Explanatory (Default)
Detailed responses with context, reasoning, and examples.

**When to use:**
- Learning new concepts
- Understanding complex codebases
- Onboarding team members
- Debugging unfamiliar issues
- Documentation tasks

**Characteristics:**
- Full explanations
- Code examples with comments
- Reasoning behind decisions
- Multiple approaches discussed
- Best practices included

**Example Response:**
```
I'll help you create a user authentication endpoint. Let me break this down:

1. First, we'll set up the route handler with Express:
   - POST /api/auth/login for handling login requests
   - Input validation using express-validator
   - Password hashing with bcrypt

2. Here's the implementation:

[Detailed code with inline comments]

This approach follows security best practices:
- Passwords are hashed with bcrypt (10 rounds)
- JWT tokens expire after 1 hour
- Rate limiting prevents brute force attacks

Alternative approaches you might consider:
- OAuth2 for social login
- Session-based auth instead of JWT
- Multi-factor authentication

Would you like me to add any of these features?
```

### Concise
Focused responses with essential information only.

**When to use:**
- Quick fixes
- Iterative development
- Context window conservation
- Experienced developers
- Time-sensitive tasks

**Characteristics:**
- Direct answers
- Minimal explanation
- Code without excessive comments
- Key points only
- No alternative approaches unless asked

**Example Response:**
```
Here's the authentication endpoint:

[Code with minimal comments]

Key points:
- bcrypt for password hashing
- JWT expires in 1 hour
- Rate limiting enabled
```

### Terse
Minimal responses with code and critical notes only.

**When to use:**
- Expert developers
- Repetitive tasks
- Maximum context efficiency
- Code-first workflows
- Rapid prototyping

**Characteristics:**
- Code only or near-code only
- Critical warnings only
- No explanations unless critical
- Assumes expert knowledge

**Example Response:**
```
[Code only]

Note: Set JWT_SECRET in .env
```

### Detailed
Comprehensive responses with in-depth analysis and documentation.

**When to use:**
- Complex architectural decisions
- Production-critical code
- Team documentation
- Code reviews
- Security-sensitive implementations

**Characteristics:**
- Extensive explanations
- Multiple code examples
- Security considerations
- Performance analysis
- Testing strategies
- Documentation
- Edge cases discussed

**Example Response:**
```
I'll implement a comprehensive authentication system with the following components:

1. Architecture Overview:
   [Detailed explanation of system design]

2. Security Considerations:
   - Password hashing: bcrypt with salt rounds
   - JWT token management and rotation
   - CSRF protection
   - Rate limiting strategies
   - Input validation and sanitization

3. Implementation:

[Multiple code blocks with extensive comments]

4. Testing Strategy:
   - Unit tests for authentication logic
   - Integration tests for API endpoints
   - Security testing for common vulnerabilities

5. Performance Considerations:
   - Database indexing for user lookups
   - Token caching strategy
   - Connection pooling

6. Edge Cases:
   - Concurrent login attempts
   - Token expiration handling
   - Account lockout after failed attempts

7. Deployment Checklist:
   - Environment variables configured
   - Database migrations run
   - Rate limiting configured
   - Monitoring and logging enabled

Would you like me to elaborate on any of these areas?
```

## Configuration

### Project-Level

Set in `.claude/settings.local.json`:

```json
{
  "outputStyle": "concise"
}
```

### Session-Level

Change during a session:

```bash
/output explanatory
/output concise
/output terse
/output detailed
```

### Per-Request

Specify in your message:

```
[concise] Create a login endpoint

[detailed] Review this authentication implementation for security issues

[terse] Add error handling to this function
```

## Style Comparison

### Same Task, Different Styles

**Task: "Add input validation to this function"**

**Explanatory:**
```
I'll add comprehensive input validation to ensure data integrity and security.

Here's the approach:
1. Validate input types
2. Check required fields
3. Sanitize user input
4. Return clear error messages

Implementation:

function processUserData(data) {
  // Validate input is an object
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid input: expected object');
  }

  // Check required fields
  const required = ['username', 'email', 'age'];
  for (const field of required) {
    if (!(field in data)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  // Validate data types
  if (typeof data.username !== 'string' || data.username.length < 3) {
    throw new Error('Username must be a string with at least 3 characters');
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    throw new Error('Invalid email format');
  }

  // Validate age is a positive number
  if (typeof data.age !== 'number' || data.age < 0) {
    throw new Error('Age must be a positive number');
  }

  // Sanitize string inputs to prevent XSS
  data.username = data.username.trim();
  data.email = data.email.trim().toLowerCase();

  return data;
}

This validation:
- Ensures type safety
- Prevents common injection attacks
- Provides clear error messages for debugging
- Sanitizes inputs before processing
```

**Concise:**
```
Added validation:

function processUserData(data) {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid input');
  }

  const required = ['username', 'email', 'age'];
  for (const field of required) {
    if (!(field in data)) throw new Error(`Missing: ${field}`);
  }

  if (typeof data.username !== 'string' || data.username.length < 3) {
    throw new Error('Invalid username');
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    throw new Error('Invalid email');
  }

  if (typeof data.age !== 'number' || data.age < 0) {
    throw new Error('Invalid age');
  }

  data.username = data.username.trim();
  data.email = data.email.trim().toLowerCase();

  return data;
}
```

**Terse:**
```
function processUserData(data) {
  if (!data || typeof data !== 'object') throw new Error('Invalid input');

  ['username', 'email', 'age'].forEach(f => {
    if (!(f in data)) throw new Error(`Missing: ${f}`);
  });

  if (typeof data.username !== 'string' || data.username.length < 3)
    throw new Error('Invalid username');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email))
    throw new Error('Invalid email');
  if (typeof data.age !== 'number' || data.age < 0)
    throw new Error('Invalid age');

  data.username = data.username.trim();
  data.email = data.email.trim().toLowerCase();
  return data;
}
```

**Detailed:**
```
I'll implement comprehensive input validation with type checking, sanitization, and security best practices.

Architecture:
- Type validation for runtime safety
- Required field checking
- Format validation with regex
- Input sanitization to prevent XSS
- Descriptive error messages

Implementation:

function processUserData(data) {
  // Type validation
  // Ensures input is an object to prevent TypeError in subsequent operations
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid input: expected object');
  }

  // Required field validation
  // Explicitly list required fields for maintainability
  const required = ['username', 'email', 'age'];
  for (const field of required) {
    if (!(field in data)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  // Username validation
  // Minimum 3 characters to prevent abuse
  // String type ensures safe string operations
  if (typeof data.username !== 'string' || data.username.length < 3) {
    throw new Error('Username must be a string with at least 3 characters');
  }

  // Email validation
  // Basic regex pattern - consider using a library like validator.js for production
  // Prevents obviously invalid emails while allowing international characters
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    throw new Error('Invalid email format');
  }

  // Age validation
  // Must be numeric and positive
  // Prevents negative ages and non-numeric values
  if (typeof data.age !== 'number' || data.age < 0) {
    throw new Error('Age must be a positive number');
  }

  // Input sanitization
  // Trim whitespace to prevent padding attacks
  // Lowercase email for consistent storage
  data.username = data.username.trim();
  data.email = data.email.trim().toLowerCase();

  return data;
}

Security Considerations:
1. Type validation prevents prototype pollution attacks
2. Input sanitization reduces XSS risk
3. Email normalization prevents duplicate accounts
4. Clear error messages aid debugging without exposing internals

Potential Improvements:
1. Use validator.js for robust email validation
2. Add username format validation (alphanumeric, etc.)
3. Implement rate limiting for repeated invalid inputs
4. Add maximum length checks to prevent DoS
5. Consider using a validation library like Joi or Zod

Testing Strategy:
- Valid inputs: should pass
- Missing fields: should throw with specific error
- Invalid types: should throw with type error
- Malicious inputs: XSS attempts, SQL injection patterns
- Edge cases: empty strings, very long inputs, Unicode characters

Example Test Cases:
processUserData({ username: 'john', email: 'john@example.com', age: 25 }); // OK
processUserData(null); // Error: Invalid input
processUserData({ username: 'ab' }); // Error: username too short
processUserData({ username: 'john', email: 'invalid', age: 25 }); // Error: invalid email
```

## Custom Formatting

### Custom Response Templates

Define custom templates:

```json
{
  "outputStyle": "custom",
  "outputTemplate": {
    "structure": [
      "summary",
      "code",
      "notes"
    ],
    "sections": {
      "summary": {
        "enabled": true,
        "maxLength": 200
      },
      "code": {
        "enabled": true,
        "comments": "minimal",
        "language": "auto"
      },
      "notes": {
        "enabled": true,
        "categories": ["security", "performance"]
      }
    }
  }
}
```

### Code Comment Density

Control comment verbosity:

```json
{
  "outputStyle": "concise",
  "codeComments": "minimal"     // none, minimal, moderate, extensive
}
```

**None:**
```javascript
function authenticate(username, password) {
  const user = db.users.find(u => u.username === username);
  if (!user) return null;
  const valid = bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;
  return jwt.sign({ id: user.id }, SECRET);
}
```

**Minimal:**
```javascript
function authenticate(username, password) {
  // Find user
  const user = db.users.find(u => u.username === username);
  if (!user) return null;

  // Verify password
  const valid = bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;

  // Generate token
  return jwt.sign({ id: user.id }, SECRET);
}
```

**Moderate:**
```javascript
/**
 * Authenticates a user with username and password
 * @param {string} username - User's username
 * @param {string} password - User's plain text password
 * @returns {string|null} JWT token or null if authentication fails
 */
function authenticate(username, password) {
  // Look up user in database
  const user = db.users.find(u => u.username === username);
  if (!user) return null;

  // Verify password against stored hash
  const valid = bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;

  // Generate and return JWT token
  return jwt.sign({ id: user.id }, SECRET);
}
```

**Extensive:**
```javascript
/**
 * Authenticates a user with username and password
 *
 * This function performs the following steps:
 * 1. Looks up the user by username in the database
 * 2. Verifies the provided password against the stored hash
 * 3. Generates a JWT token if authentication succeeds
 *
 * @param {string} username - User's username (case-sensitive)
 * @param {string} password - User's plain text password
 * @returns {string|null} JWT token containing user ID if successful, null otherwise
 *
 * @example
 * const token = authenticate('john', 'secret123');
 * if (token) {
 *   // User authenticated successfully
 * }
 */
function authenticate(username, password) {
  // Look up user in database by username
  // Returns null if user not found
  const user = db.users.find(u => u.username === username);
  if (!user) return null;

  // Verify password against stored hash using bcrypt
  // bcrypt automatically handles salt comparison
  const valid = bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;

  // Generate JWT token with user ID as payload
  // Token is signed with SECRET key for verification
  return jwt.sign({ id: user.id }, SECRET);
}
```

## Context Management

### Output Style Impact on Context

Different styles use different amounts of context:

**Token Usage Example (approximate):**
- Terse: 50-100 tokens
- Concise: 100-300 tokens
- Explanatory: 300-800 tokens
- Detailed: 800-2000+ tokens

**Strategy for long sessions:**

```json
{
  "outputStyle": "concise",
  "contextManagement": {
    "autoCompact": true,
    "compactThreshold": 80,
    "preserveRecent": 5
  }
}
```

### Dynamic Style Switching

Switch styles based on context usage:

```json
{
  "outputStyle": "explanatory",
  "dynamicStyling": {
    "enabled": true,
    "rules": [
      {
        "when": "contextUsage > 80%",
        "switchTo": "concise"
      },
      {
        "when": "contextUsage > 90%",
        "switchTo": "terse"
      }
    ]
  }
}
```

## Workflow-Specific Styles

### Development Phases

**Exploration/Learning:**
```json
{
  "outputStyle": "explanatory",
  "codeComments": "extensive"
}
```

**Active Development:**
```json
{
  "outputStyle": "concise",
  "codeComments": "moderate"
}
```

**Debugging:**
```json
{
  "outputStyle": "detailed",
  "includeDebugging": true
}
```

**Refactoring:**
```json
{
  "outputStyle": "concise",
  "focusOn": ["changes", "rationale"]
}
```

**Code Review:**
```json
{
  "outputStyle": "detailed",
  "includeAnalysis": true,
  "categories": ["security", "performance", "maintainability"]
}
```

## Language-Specific Formatting

### Python

```json
{
  "languageFormatting": {
    "python": {
      "docstringStyle": "google",    // google, numpy, sphinx
      "typeHints": true,
      "comments": "moderate"
    }
  }
}
```

**Example output:**
```python
def authenticate(username: str, password: str) -> Optional[str]:
    """Authenticate user with username and password.

    Args:
        username: User's username
        password: User's plain text password

    Returns:
        JWT token if authentication succeeds, None otherwise
    """
    user = db.users.find_one({'username': username})
    if not user:
        return None

    if not bcrypt.verify(password, user['password_hash']):
        return None

    return jwt.encode({'id': user['id']}, SECRET)
```

### TypeScript

```json
{
  "languageFormatting": {
    "typescript": {
      "jsdocStyle": "tsdoc",
      "includeTypes": true,
      "comments": "moderate"
    }
  }
}
```

**Example output:**
```typescript
/**
 * Authenticates a user with username and password
 * @param username - User's username
 * @param password - User's plain text password
 * @returns JWT token or null if authentication fails
 */
function authenticate(username: string, password: string): string | null {
  const user = db.users.find(u => u.username === username);
  if (!user) return null;

  const valid = bcrypt.compare(password, user.passwordHash);
  if (!valid) return null;

  return jwt.sign({ id: user.id }, SECRET);
}
```

## Best Practices

### Choosing the Right Style

**Use Explanatory when:**
- Learning a new technology
- Working with junior developers
- Documenting complex logic
- Making architectural decisions

**Use Concise when:**
- You're experienced with the tech stack
- Iterating quickly
- Context window is filling up
- Working on straightforward tasks

**Use Terse when:**
- You're an expert
- Doing repetitive tasks
- Maximizing context efficiency
- Speed is critical

**Use Detailed when:**
- Reviewing security-critical code
- Making production changes
- Creating documentation
- Handling complex edge cases

### Style Switching Strategies

**Start detailed, then concise:**
```
Day 1: /output detailed      # Learn the codebase
Day 2-3: /output explanatory # Understand patterns
Day 4+: /output concise      # Productive development
```

**Context-aware switching:**
```
New feature: /output explanatory
Bug fix: /output concise
Security review: /output detailed
Quick change: /output terse
```

### Team Configurations

**Team standard:**
```json
{
  "outputStyle": "concise",
  "codeComments": "moderate",
  "documentation": {
    "style": "explanatory"
  }
}
```

**Individual overrides:**
```json
{
  "extends": ".claude/settings.shared.json",
  "outputStyle": "terse"  // Personal preference
}
```

## Troubleshooting

### Responses Too Verbose

```json
{
  "outputStyle": "concise",
  "maxResponseLength": 500
}
```

Or use session command:
```
/output concise
```

### Responses Too Brief

```json
{
  "outputStyle": "explanatory",
  "minExplanationLength": 200
}
```

Or request more detail:
```
[detailed] Explain this implementation
```

### Inconsistent Formatting

Lock the style:
```json
{
  "outputStyle": "concise",
  "allowStyleOverride": false
}
```

## Advanced Configuration

### Conditional Formatting

```json
{
  "conditionalFormatting": {
    "rules": [
      {
        "when": {
          "fileType": "*.test.ts",
          "action": "create"
        },
        "style": "concise",
        "includeTestExamples": true
      },
      {
        "when": {
          "fileType": "*.md",
          "action": "write"
        },
        "style": "detailed",
        "format": "markdown"
      },
      {
        "when": {
          "securityRelated": true
        },
        "style": "detailed",
        "includeSecurityNotes": true
      }
    ]
  }
}
```

### Output Filtering

```json
{
  "outputFilters": {
    "excludeSections": ["alternatives", "examples"],
    "includeSections": ["summary", "code", "warnings"]
  }
}
```

### Response Structure

```json
{
  "responseStructure": {
    "format": "structured",
    "sections": [
      {
        "name": "summary",
        "maxLines": 5,
        "required": true
      },
      {
        "name": "implementation",
        "required": true
      },
      {
        "name": "notes",
        "required": false
      }
    ]
  }
}
```

## Next Steps

- [Permissions Configuration](./permissions.md) - Control what Claude Code can do
- [Quality Gates](./quality-gates.md) - Set quality requirements
- [Advanced Configuration](./advanced-config.md) - Advanced features
- [Best Practices](../best-practices/README.md) - Development workflows
