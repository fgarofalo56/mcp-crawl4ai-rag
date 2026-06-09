# 🔀 Git Operations Commands

> **Git workflow and operations commands**

Git operations commands streamline version control workflows from committing to pull requests and conflict resolution.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/smart-commit](#smart-commit---intelligent-commit-creation)
  - [/create-pr](#create-pr---create-pull-request)
  - [/conflict-resolver](#conflict-resolver---resolve-merge-conflicts)
  - [/new-dev-branch](#new-dev-branch---create-development-branch)
  - [/git-cleanup](#git-cleanup---clean-up-branches)
  - [/commit-push-pr](#commit-push-pr---commit-push-and-create-pr)
- [Workflow Patterns](#-workflow-patterns)

---

## 📋 Command Reference

### /smart-commit - Intelligent Commit Creation

**Purpose**: Analyzes changes and creates conventional commits with appropriate types.

**Execution Time**: 30-60 seconds

**Resources**: Low

#### What It Does

1. **Analyzes Changes**
   - Reviews git diff
   - Identifies change types
   - Categorizes modifications

2. **Determines Commit Type**
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation
   - `refactor:` - Code refactoring
   - `test:` - Test additions
   - `chore:` - Maintenance

3. **Generates Commit Message**
   - Clear, concise summary
   - Detailed body (if needed)
   - References issues
   - Follows conventions

4. **Creates Commit**
   - Stages appropriate files
   - Creates commit
   - Shows summary

#### Usage Examples

```bash
# Analyze and commit current changes
/smart-commit

# Commit with custom message prefix
/smart-commit "Add user authentication"

# Commit with issue reference
/smart-commit --issue #123

# Commit staged files only
/smart-commit --staged
```

#### Expected Output

```
🔍 Analyzing Changes...

📊 Changes Summary:
  Modified: 3 files
  Added: 2 files
  Deleted: 0 files

📝 Change Type: feat (new feature)

💡 Suggested Commit Message:

feat: add user email verification

- Implement email verification endpoint
- Add email sending service with Azure Communication Services
- Update user model with verification fields
- Add comprehensive tests with 95% coverage

Closes #123

✅ Create this commit? (Y/n):
```

---

### /create-pr - Create Pull Request

**Purpose**: Creates well-structured pull requests with proper branch management and PR templates.

**Execution Time**: 1-2 minutes

**Resources**: Medium

#### What It Does

1. **Validates Branch**
   - Checks current branch
   - Ensures not on main/master
   - Verifies commits exist

2. **Analyzes Changes**
   - Reviews all commits
   - Generates PR summary
   - Identifies files changed

3. **Creates PR Template**
   - Summary of changes
   - Test plan
   - Breaking changes
   - Issue references

4. **Pushes and Creates PR**
   - Pushes branch to remote
   - Creates GitHub PR
   - Returns PR URL

#### Usage Examples

```bash
# Create PR from current branch
/create-pr

# Create PR with custom title
/create-pr "Add user authentication feature"

# Create draft PR
/create-pr --draft

# Create PR with specific base branch
/create-pr --base develop
```

#### Expected Output

```
🔍 Preparing Pull Request...

📊 Branch Analysis:
  Current: feature/user-email-verification
  Base: develop
  Commits: 5 ahead

📝 PR Summary Generated:

## Summary
Implements user email verification functionality

- Email verification endpoint
- Azure Communication Services integration
- User model updates
- Comprehensive test coverage

## Test Plan
- [x] Unit tests (95% coverage)
- [x] Integration tests
- [x] Manual testing in dev environment
- [ ] Security review needed

## Breaking Changes
None

Closes #123

🚀 Pushing branch...
✅ Branch pushed to origin

📬 Creating Pull Request...
✅ PR Created!

🔗 URL: https://github.com/org/repo/pull/456

💡 Next Steps:
  - Request reviews
  - Monitor CI/CD pipeline
  - Address feedback
```

---

### /conflict-resolver - Resolve Merge Conflicts

**Purpose**: Intelligent merge conflict resolution with semantic conflict detection.

**Execution Time**: 2-5 minutes

**Resources**: Medium

#### What It Does

1. **Detects Conflicts**
   - Lists conflicted files
   - Analyzes conflict types
   - Categorizes by complexity

2. **Analyzes Context**
   - Reviews both branches
   - Understands intent
   - Identifies semantic conflicts

3. **Suggests Resolutions**
   - Recommended resolution
   - Alternative approaches
   - Manual review points

4. **Applies Resolution**
   - Resolves conflicts
   - Tests resolution
   - Creates merge commit

#### Usage Examples

```bash
# Resolve all conflicts
/conflict-resolver

# Resolve with specific strategy
/conflict-resolver --strategy safe

# Resolve specific file
/conflict-resolver src/api/users.py

# Interactive resolution
/conflict-resolver --interactive
```

---

### /new-dev-branch - Create Development Branch

**Purpose**: Creates new development branch from latest develop/main.

**Execution Time**: 5-15 seconds

**Resources**: Low

#### Usage Examples

```bash
# Create feature branch
/new-dev-branch feature/user-auth

# Create bugfix branch
/new-dev-branch bugfix/login-error

# Create from specific branch
/new-dev-branch feature/new-api --from develop

# Create and push
/new-dev-branch feature/payments --push
```

---

### /git-cleanup - Clean Up Branches

**Purpose**: Cleans up merged and stale branches.

**Execution Time**: 30-60 seconds

**Resources**: Low

#### Usage Examples

```bash
# Clean up merged branches
/git-cleanup

# Show what would be deleted (dry run)
/git-cleanup --dry-run

# Clean up remote branches too
/git-cleanup --remote

# Keep branches newer than N days
/git-cleanup --keep-days 30
```

---

### /commit-push-pr - Commit, Push, and Create PR

**Purpose**: Complete workflow from commit to PR in one command.

**Execution Time**: 1-3 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Complete workflow
/commit-push-pr

# With custom message
/commit-push-pr "Add new feature"

# Create draft PR
/commit-push-pr --draft
```

---

## 🔄 Workflow Patterns

### Feature Development Workflow

```bash
# 1. Create feature branch
/new-dev-branch feature/user-notifications

# 2. ... make changes ...

# 3. Review changes
/review-staged

# 4. Smart commit
/smart-commit

# 5. Create PR
/create-pr
```

### Bugfix Workflow

```bash
# 1. Create bugfix branch
/new-dev-branch bugfix/auth-error

# 2. ... fix bug ...

# 3. Test fix
/test-run

# 4. Complete workflow
/commit-push-pr "Fix authentication error"
```

### Conflict Resolution Workflow

```bash
# 1. Attempt merge
git merge develop

# 2. Conflicts detected
/conflict-resolver

# 3. Verify resolution
/test-run

# 4. Complete merge
git commit
```

---

**Navigate**: [← Testing & QA](./testing-qa.md) | [Commands Home](./README.md) | [Advanced Workflows →](./advanced-workflows.md)

---

*Git it done*
