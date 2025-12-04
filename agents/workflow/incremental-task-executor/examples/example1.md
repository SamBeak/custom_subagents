# Example 1: Basic Incremental Execution

## Scenario
A developer has a task list from `prd-task-generator` and wants to implement the feature incrementally with proper testing and commits.

## Input
```
Task with subagent_type: incremental-task-executor
Prompt: "Execute tasks from /tasks/tasks-prd-login-form.md"
```

## Initial Task List State

File: `/tasks/tasks-prd-login-form.md`

```markdown
## Relevant Files

### Notes

- Run tests with: `npm test`
- Use existing Button and Input components

## Tasks

- [ ] 1.0 Create authentication service
  - [ ] 1.1 Add login API method
  - [ ] 1.2 Add logout API method
  - [ ] 1.3 Add session management

- [ ] 2.0 Build login form component
  - [ ] 2.1 Create LoginForm component
  - [ ] 2.2 Add form validation
  - [ ] 2.3 Add error handling

- [ ] 3.0 Write tests
  - [ ] 3.1 Test authentication service
  - [ ] 3.2 Test LoginForm component
```

## Execution Flow

### Step 1: Agent Initialization

```
Agent: Reading task list from /tasks/tasks-prd-login-form.md...
Agent: Found 3 parent tasks with 8 total sub-tasks
Agent: 0 tasks completed, 8 remaining
Agent:
Agent: Next task is 1.1: Add login API method
Agent: Ready to begin? (yes/y)
```

**User:** `yes`

### Step 2: First Sub-Task Execution

```
Agent: Implementing Task 1.1: Add login API method
Agent:
Agent: [Creates src/lib/api/auth.ts]
Agent:
Agent: Created file: src/lib/api/auth.ts
Agent: Added login method with:
Agent: - Email/password parameters
Agent: - API endpoint call
Agent: - Error handling
Agent: - TypeScript types
Agent:
Agent: Updating task list...
Agent: ✓ Task 1.1 marked complete
Agent:
Agent: Updated Relevant Files section:
Agent: + src/lib/api/auth.ts - Authentication API methods
Agent:
Agent: Progress: 1/8 sub-tasks complete
Agent: Ready to proceed to Task 1.2? (yes/y)
```

**User:** `yes`

### Step 3: Second Sub-Task

```
Agent: Implementing Task 1.2: Add logout API method
Agent:
Agent: [Updates src/lib/api/auth.ts]
Agent:
Agent: Modified: src/lib/api/auth.ts
Agent: Added logout method with:
Agent: - Session clearing
Agent: - API call to /api/auth/logout
Agent: - Cleanup logic
Agent:
Agent: ✓ Task 1.2 marked complete
Agent:
Agent: Progress: 2/8 sub-tasks complete
Agent: Ready to proceed to Task 1.3? (yes/y)
```

**User:** `yes`

### Step 4: Last Sub-Task of Parent 1.0

```
Agent: Implementing Task 1.3: Add session management
Agent:
Agent: [Updates src/lib/api/auth.ts]
Agent:
Agent: Modified: src/lib/api/auth.ts
Agent: Added session management:
Agent: - Token storage in localStorage
Agent: - Token refresh logic
Agent: - Session validation
Agent:
Agent: ✓ Task 1.3 marked complete
Agent:
Agent: All sub-tasks under 1.0 are complete!
Agent: Running test suite before committing...
```

### Step 5: Testing and Commit

```
Agent: $ npm test
Agent:
Agent: > project@1.0.0 test
Agent: > jest
Agent:
Agent:  PASS  src/lib/api/auth.test.ts
Agent:    Authentication API
Agent:      ✓ login calls correct endpoint (23ms)
Agent:      ✓ logout clears session (15ms)
Agent:      ✓ handles network errors (18ms)
Agent:
Agent: Test Suites: 1 passed, 1 total
Agent: Tests:       3 passed, 3 total
Agent: Time:        2.156s
Agent:
Agent: ✓ All tests passed
Agent:
Agent: Staging changes...
Agent: $ git add .
Agent:
Agent: Cleaning up temporary files...
Agent: (No temporary files found)
Agent:
Agent: Creating conventional commit...
Agent: $ git commit -m "feat: implement authentication API service" \
Agent:                -m "- Add login method with email/password auth" \
Agent:                -m "- Add logout method with session cleanup" \
Agent:                -m "- Add session management with token refresh" \
Agent:                -m "Completes Task 1.0 from PRD-login-form"
Agent:
Agent: [main 3a7f2e1] feat: implement authentication API service
Agent:  2 files changed, 156 insertions(+)
Agent:  create mode 100644 src/lib/api/auth.ts
Agent:  create mode 100644 src/lib/api/auth.test.ts
Agent:
Agent: ✓ Parent task 1.0 marked complete
Agent:
Agent: Progress: 3/8 sub-tasks, 1/3 parent tasks complete
Agent: Next task is 2.1: Create LoginForm component
Agent: Ready to proceed? (yes/y)
```

**User:** `yes`

### Step 6: Continue with Task 2.0

```
Agent: Implementing Task 2.1: Create LoginForm component
Agent:
Agent: [Creates src/components/LoginForm.tsx]
Agent:
Agent: Created: src/components/LoginForm.tsx
Agent: Added:
Agent: - Email and password input fields
Agent: - Submit button with loading state
Agent: - Form state management
Agent: - Integration with auth API
Agent:
Agent: ✓ Task 2.1 marked complete
Agent:
Agent: Updated Relevant Files:
Agent: + src/components/LoginForm.tsx - Login form component
Agent:
Agent: Progress: 4/8 sub-tasks complete
Agent: Ready to proceed to Task 2.2? (yes/y)
```

**User:** `yes`

[Process continues through remaining tasks...]

## Final Task List State

After all tasks complete:

```markdown
## Relevant Files

- `src/lib/api/auth.ts` - Authentication API methods
- `src/lib/api/auth.test.ts` - Tests for auth API
- `src/components/LoginForm.tsx` - Login form component
- `src/components/LoginForm.test.tsx` - Tests for LoginForm
- `src/lib/validation/formValidation.ts` - Form validation logic
- `src/lib/validation/formValidation.test.ts` - Validation tests

### Notes

- Run tests with: `npm test`
- Use existing Button and Input components

## Tasks

- [x] 1.0 Create authentication service
  - [x] 1.1 Add login API method
  - [x] 1.2 Add logout API method
  - [x] 1.3 Add session management

- [x] 2.0 Build login form component
  - [x] 2.1 Create LoginForm component
  - [x] 2.2 Add form validation
  - [x] 2.3 Add error handling

- [x] 3.0 Write tests
  - [x] 3.1 Test authentication service
  - [x] 3.2 Test LoginForm component
```

## Git History

```bash
$ git log --oneline

6d8a9b2 (HEAD -> main) test: add comprehensive test coverage
3c5f1a8 feat: implement login form UI with validation
3a7f2e1 feat: implement authentication API service
```

Each commit:
- ✅ Follows conventional commit format
- ✅ Has descriptive summary
- ✅ Lists key changes in body
- ✅ References task and PRD
- ✅ Passed all tests before commit

## Benefits Demonstrated

### 1. **Controlled Progress**
- User approved each step
- Could review code at any point
- Easy to pause and resume

### 2. **Quality Assurance**
- Tests run before every commit
- No broken code committed
- Clean git history

### 3. **Accurate Tracking**
- Task list always current
- File list maintained
- Clear progress visibility

### 4. **Professional Commits**
- Conventional format
- Descriptive messages
- Logical groupings
- Easy to understand history

### 5. **Efficient Workflow**
- No manual checkbox updates
- Automated testing
- Automatic file tracking
- Reduced cognitive load

## Time Comparison

### Without Agent (Manual)
- Check task list: 30s
- Implement task: 15 min
- Manually update checkbox: 30s
- Manually update files list: 1 min
- Run tests: 1 min
- Stage files: 30s
- Write commit message: 2 min
- Commit: 30s

**Per sub-task: ~21 minutes**
**For 8 sub-tasks: ~168 minutes (2.8 hours)**

Plus potential for:
- Forgetting to update task list
- Forgetting to run tests
- Poor commit messages
- Missing file updates

### With Agent (Automated)
- Implement task: 15 min
- Agent handles everything else automatically

**Per sub-task: ~15 minutes**
**For 8 sub-tasks: ~120 minutes (2 hours)**

Plus guarantees:
- Task list always updated
- Tests always run
- Quality commit messages
- Accurate file tracking

**Time saved: 48 minutes (28%)**
**Quality improved: 100%**

## Key Takeaways

1. **One task at a time** prevents overwhelming changes
2. **User approval** ensures quality control
3. **Automated testing** catches issues early
4. **Conventional commits** create professional history
5. **Automated tracking** reduces manual overhead

## Perfect For

- Junior developers learning workflow discipline
- Teams wanting consistent git history
- Projects requiring high code quality
- Anyone who wants systematic progress tracking
- Preventing "I forgot to run tests" scenarios
