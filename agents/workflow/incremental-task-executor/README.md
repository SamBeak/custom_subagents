# Incremental Task Executor

## Overview
A workflow orchestration agent that executes task lists in a controlled, incremental manner. Enforces disciplined development through one-task-at-a-time execution, automated testing, proper git commits, and comprehensive task list maintenance.

## Category
workflow

## Capabilities
- Execute tasks incrementally with user approval between each sub-task
- Automatically update task list checkboxes as work progresses
- Run test suites after completing parent tasks
- Create conventional commit messages automatically
- Manage git workflow (staging, committing)
- Maintain "Relevant Files" section with accurate file listings
- Clean up temporary files before commits
- Enforce development discipline and quality standards

## Tools Available
- **Read**: Load task lists and source files
- **Write**: Create new files as needed
- **Edit**: Update task lists and modify existing files
- **Glob**: Find project files and understand structure
- **Grep**: Search for patterns in codebase
- **Bash**: Run tests, git commands, cleanup operations

## Usage

### Basic Example

```
Task with subagent_type: incremental-task-executor
Prompt: "Execute tasks from /tasks/tasks-prd-user-profile.md"
```

**Agent Workflow:**
1. Reads task list
2. Finds first uncompleted sub-task
3. Asks: "Next task is 1.1: Create validation function. Ready to begin? (yes/y)"
4. Waits for your "yes"
5. Implements task 1.1
6. Updates checkbox to `[x]`
7. Asks: "Ready to proceed to 1.2? (yes/y)"
8. Repeats until parent task complete
9. Runs tests, commits, marks parent task complete
10. Continues to next parent task

### Resume Execution

```
Task with subagent_type: incremental-task-executor
Prompt: "Resume execution of /tasks/tasks-prd-dashboard.md from where we left off"
```

The agent will:
- Read current task list state
- Find first uncompleted sub-task
- Summarize progress so far
- Ask for approval to continue
- Resume incremental execution

## Key Features

### 1. One Sub-Task at a Time

The agent will NEVER execute multiple sub-tasks without your explicit approval.

```
Agent: Task 1.1 completed ✓
Agent: Ready to proceed to 1.2? (yes/y)
[WAITS for your response]
```

This ensures:
- You can review progress incrementally
- Easy to pause and resume
- Prevents overwhelming changes
- Allows course correction at any point

### 2. Automated Task List Updates

Checkboxes are updated automatically:

**Before:**
```markdown
- [ ] 1.0 Create validation module
  - [ ] 1.1 Add email validation
  - [ ] 1.2 Add phone validation
```

**After completing 1.1:**
```markdown
- [ ] 1.0 Create validation module
  - [x] 1.1 Add email validation
  - [ ] 1.2 Add phone validation
```

**After completing all sub-tasks:**
```markdown
- [x] 1.0 Create validation module
  - [x] 1.1 Add email validation
  - [x] 1.2 Add phone validation
```

### 3. Testing Before Commits

When all sub-tasks under a parent are complete:

1. **Run full test suite**
   ```bash
   npm test  # or pytest, rspec, mvn test, etc.
   ```

2. **Only proceed if tests pass**
   - All tests must pass
   - If failures occur, fixes them first
   - Re-runs tests until all pass

3. **Then stage and commit**
   ```bash
   git add .
   git commit -m "feat: ..." -m "- detail 1" -m "- detail 2"
   ```

### 4. Conventional Commits

Commits follow conventional commit format:

```bash
git commit \
  -m "feat: implement user profile validation" \
  -m "- Add email format validation" \
  -m "- Add phone number sanitization" \
  -m "- Include comprehensive unit tests" \
  -m "Completes Task 2.0 from PRD-user-profile"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `docs:` - Documentation
- `style:` - Code style/formatting
- `chore:` - Maintenance tasks

### 5. Cleanup Before Commits

Before creating commit:
- Removes temporary files (`.tmp`, `.backup`)
- Removes debug code and console.logs
- Removes commented-out code
- Ensures clean staging area

### 6. Relevant Files Maintenance

The "Relevant Files" section stays current:

```markdown
## Relevant Files

- `src/lib/validation.ts` - User input validation functions
- `src/lib/validation.test.ts` - Tests for validation module
- `src/components/ProfileForm.tsx` - Modified to use validation
```

Files are added/updated automatically as work progresses.

## Workflow Example

### Starting Fresh

```
User: Execute tasks from /tasks/tasks-prd-payment.md

Agent: Reading task list...
Agent: Found 3 parent tasks with 15 total sub-tasks
Agent: Next task is 1.1: Create payment data types
Agent: Ready to begin? (yes/y)

User: yes

Agent: [creates src/types/payment.ts with type definitions]
Agent: Task 1.1 completed ✓
Agent: Updated task list
Agent: Created: src/types/payment.ts
Agent: Ready to proceed to 1.2? (yes/y)

User: yes

Agent: [implements 1.2]
...continues...
```

### Completing a Parent Task

```
Agent: Task 1.3 completed ✓
Agent: All sub-tasks under 1.0 are now complete
Agent: Running test suite...
Agent: $ npm test
Agent:
Agent: ✓ All tests passed (24/24)
Agent:
Agent: Staging changes...
Agent: $ git add .
Agent:
Agent: Cleaning up temporary files...
Agent: Removed: validation.test.ts.tmp
Agent:
Agent: Creating commit...
Agent: $ git commit -m "feat: implement payment data types" -m "- Add PaymentMethod interface" -m "- Add Transaction type" -m "- Add validation helper types" -m "Completes Task 1.0 from PRD-payment"
Agent:
Agent: [main abc1234] feat: implement payment data types
Agent:  3 files changed, 87 insertions(+)
Agent:
Agent: ✓ Parent task 1.0 marked complete
Agent:
Agent: Next task is 2.1: Create payment API client
Agent: Ready to proceed? (yes/y)
```

### Handling Test Failures

```
Agent: Task 2.3 completed ✓
Agent: All sub-tasks under 2.0 complete
Agent: Running test suite...
Agent: $ npm test
Agent:
Agent: ✗ Test failures (3 failed, 21 passed)
Agent:
Agent: Failures:
Agent: - payment.test.ts: validateCardNumber fails for Amex
Agent: - payment.test.ts: validateExpiry rejects valid dates
Agent: - api.test.ts: timeout on mock server
Agent:
Agent: Fixing test failures...
Agent: [analyzes failures and fixes issues]
Agent:
Agent: Re-running tests...
Agent: $ npm test
Agent:
Agent: ✓ All tests passed (24/24)
Agent:
Agent: [proceeds with commit]
```

## Input/Output Format

### Input
- **Task List Path**: Path to Markdown task list file
- **Optional Context**: "Resume from where we left off" or "Start fresh"

**Example:**
```
Execute tasks from /tasks/tasks-prd-authentication.md
```

### Output

The agent provides:

1. **Progress Updates**
   ```
   Task 1.1 completed ✓
   Created: src/auth/service.ts
   ```

2. **Test Results**
   ```
   Running tests...
   ✓ All tests passed (30/30)
   ```

3. **Commit Summaries**
   ```
   Committed: feat: implement authentication service
   Files changed: 4 files, 235 insertions(+)
   ```

4. **Approval Requests**
   ```
   Ready to proceed to 1.2? (yes/y)
   ```

5. **Updated Task List**
   The original task list file is updated with checkboxes marked

## Best Practices

### 1. Review After Each Task
```
Agent: Task 1.1 completed ✓
Agent: Ready for 1.2? (yes/y)

User: Let me review first
[reviews code]
User: yes
```

### 2. Provide Context When Starting
```
Good: Execute tasks from /tasks/tasks-prd-profile.md starting fresh
Better: Execute /tasks/tasks-prd-profile.md. Use existing Auth service from src/lib/auth
```

### 3. Resume Properly
```
Resume execution of /tasks/tasks-prd-dashboard.md from Task 2.3
```

### 4. Pause When Needed
```
Agent: Ready for 3.2? (yes/y)
User: no, pause here
Agent: Paused at 3.2. Resume anytime with "yes"
```

### 5. Check Progress
```
What's the current status of /tasks/tasks-prd-payment.md?

Agent will show:
- Tasks completed: 1.0, 2.0
- Current task: 3.1
- Remaining: 3.2, 3.3, 4.0, 5.0
```

## Common Workflows

### Workflow 1: Complete Feature Implementation
```
1. Start: Execute tasks from /tasks/tasks-prd-feature.md
2. Agent implements 1.1, asks approval
3. User: yes
4. Agent implements 1.2, asks approval
5. User: yes
6. Agent implements 1.3 (last sub-task)
7. Agent runs tests → passes
8. Agent commits Task 1.0
9. Agent moves to 2.1
10. Repeat until all tasks complete
```

### Workflow 2: Daily Development Session
```
Morning:
  Resume /tasks/tasks-prd-dashboard.md

  Agent: Previously completed: 1.0, 2.0
  Agent: Next task: 3.1
  Agent: Ready to continue? (yes/y)

[Work session]

Evening (5 PM):
  Agent: Ready for 4.3? (yes/y)
  User: no, stopping for today

Next Morning:
  Resume /tasks/tasks-prd-dashboard.md

  Agent: Last completed: 4.2
  Agent: Next: 4.3
  Agent: Ready? (yes/y)
```

### Workflow 3: Handle Unexpected Issues
```
Agent: Task 2.2 completed ✓
Agent: All sub-tasks complete, running tests...
Agent: ✗ Tests failed

[Agent fixes issues]

Agent: Re-running tests...
Agent: ✓ Tests passed
Agent: Committed: fix: resolve validation edge cases
Agent: Parent 2.0 complete
Agent: Ready for 3.1? (yes/y)
```

## Troubleshooting

### Agent Moves Too Fast
**Problem:** Agent doesn't wait for approval

**This shouldn't happen** - agent is programmed to always wait. If it does:
- Restart agent
- Re-invoke with explicit: "One task at a time, wait for my approval"

### Tests Keep Failing
**Problem:** Tests fail repeatedly

**Agent will:**
- Show exact failures
- Attempt fixes
- Re-run tests
- Not commit until tests pass

**You can:**
- Review failures
- Provide guidance: "Skip integration tests, run unit tests only"
- Fix manually and tell agent to continue

### Wrong File Paths
**Problem:** Agent creates files in wrong location

**Prevention:**
- Task list should have correct paths in "Relevant Files"
- Provide context: "Create files in src/features/ not src/components/"

**Fix:**
- Pause agent
- Fix file locations manually
- Resume with: "Continue from current task"

### Unclear Next Task
**Problem:** Task list has ambiguous next task

**Agent will:**
- Identify the issue
- Ask for clarification
- Wait for instruction

**You should:**
- Clarify which task to do
- Update task list if needed
- Tell agent to proceed

### Git Conflicts
**Problem:** Commit fails due to conflicts

**Agent will:**
- Alert you immediately
- Not attempt auto-resolution
- Wait for instructions

**You should:**
- Resolve conflicts manually
- Tell agent: "Conflicts resolved, continue"

## Integration with Other Agents

### Works Great With

**prd-task-generator** → **incremental-task-executor**
```
1. prd-task-generator creates task list
2. incremental-task-executor executes it step-by-step
```

**Code Review Agents**
```
1. incremental-task-executor completes task
2. Code review agent reviews the changes
3. Fixes applied if needed
4. incremental-task-executor continues
```

**Testing Agents**
```
1. incremental-task-executor asks for approval
2. Testing agent runs additional checks
3. Approval given if checks pass
4. incremental-task-executor continues
```

## Advanced Features

### Custom Test Commands

Default behavior:
```
npm test  # for Node projects
pytest    # for Python
rspec     # for Ruby
```

Override:
```
Execute /tasks/tasks.md using "npm run test:unit" for tests
```

### Skip Testing (Not Recommended)

Only in special cases:
```
Execute /tasks/tasks.md and skip testing for now
```

Agent will still commit but won't run tests.

### Batch Approval (Not Recommended)

For very simple tasks:
```
Execute /tasks/tasks.md with auto-approval for sub-tasks under 2.0
```

Agent will auto-approve sub-tasks 2.1, 2.2, etc. but still wait at parent tasks.

## Limitations

### What This Agent Does
- ✅ Executes task lists incrementally
- ✅ Updates checkboxes automatically
- ✅ Runs tests before commits
- ✅ Creates conventional commits
- ✅ Maintains file listings
- ✅ Enforces workflow discipline

### What This Agent Does NOT Do
- ❌ Create task lists (use prd-task-generator)
- ❌ Design solutions (expects clear tasks)
- ❌ Make architectural decisions
- ❌ Resolve merge conflicts automatically
- ❌ Deploy or release code
- ❌ Create pull requests

## Version History

### v1.0.0
- Initial release
- Incremental task execution with user approval
- Automated testing before commits
- Conventional commit message generation
- Task list maintenance
- Relevant files tracking
- Cleanup automation

## Author
Custom Subagents Repository

---

**Perfect For:**
- Systematic feature implementation
- Teaching junior developers workflow discipline
- Maintaining code quality throughout development
- Preventing "works on my machine" scenarios
- Creating clean git history

**Need help?** Check the [Troubleshooting Guide](../../../docs/troubleshooting.md) or [Best Practices](../../../docs/best-practices.md).
