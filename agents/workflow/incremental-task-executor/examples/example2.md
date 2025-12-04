# Example 2: Handling Test Failures and Recovery

## Scenario
During feature implementation, tests fail after completing a parent task. The agent must fix the failures before committing.

## Input
```
Task with subagent_type: incremental-task-executor
Prompt: "Execute tasks from /tasks/tasks-prd-payment-validation.md"
```

## Task List (Simplified)

```markdown
## Tasks

- [ ] 1.0 Implement credit card validation
  - [ ] 1.1 Add card number validation
  - [ ] 1.2 Add expiry date validation
  - [ ] 1.3 Add CVV validation

- [ ] 2.0 Add payment amount validation
  - [ ] 2.1 Validate amount range
  - [ ] 2.2 Validate currency format
```

## Execution Flow

### Tasks 1.1 - 1.3 Complete Successfully

```
[Agent completes 1.1, 1.2, 1.3 with user approval at each step]

Agent: ✓ Task 1.3 completed
Agent: All sub-tasks under 1.0 are complete!
Agent: Running test suite before committing...
```

### Test Failure Detected

```
Agent: $ npm test
Agent:
Agent: > payment-app@1.0.0 test
Agent: > jest
Agent:
Agent:  PASS  src/lib/validation/cardNumber.test.ts
Agent:  PASS  src/lib/validation/cvv.test.ts
Agent:  FAIL  src/lib/validation/expiry.test.ts
Agent:    Credit Card Expiry Validation
Agent:      ✓ accepts valid future dates (18ms)
Agent:      ✓ rejects past dates (12ms)
Agent:      ✗ validates month range (45ms)
Agent:      ✗ handles edge case: December (23ms)
Agent:      ✓ rejects invalid format (15ms)
Agent:
Agent:    ● Credit Card Expiry Validation › validates month range
Agent:
Agent:      expect(received).toBe(expected)
Agent:
Agent:      Expected: false
Agent:      Received: true
Agent:
Agent:        24 |   it('validates month range', () => {
Agent:        25 |     expect(validateExpiry('13/25')).toBe(false);
Agent:      > 26 |     expect(validateExpiry('00/25')).toBe(false);
Agent:           |                                     ^
Agent:        27 |   });
Agent:
Agent:    ● Credit Card Expiry Validation › handles edge case: December
Agent:
Agent:      expect(received).toBe(expected)
Agent:
Agent:      Expected: true
Agent:      Received: false
Agent:
Agent:        31 |   it('handles edge case: December', () => {
Agent:      > 32 |     expect(validateExpiry('12/25')).toBe(true);
Agent:           |                                     ^
Agent:        33 |   });
Agent:
Agent: Test Suites: 1 failed, 2 passed, 3 total
Agent: Tests:       2 failed, 5 passed, 7 total
Agent:
Agent: ✗ Tests failed (2 failures detected)
Agent:
Agent: Cannot commit with failing tests. Analyzing failures...
```

### Agent Analyzes and Fixes

```
Agent: Analyzing test failures:
Agent:
Agent: Issue 1: validateExpiry('00/25') returns true, should be false
Agent:   - Month 00 is invalid (months are 01-12)
Agent:   - Current code doesn't check for month < 1
Agent:
Agent: Issue 2: validateExpiry('12/25') returns false, should be true
Agent:   - December (12) is valid
Agent:   - Current code has off-by-one error (checking > 12 instead of > 12)
Agent:
Agent: Root cause: Incorrect month range validation in src/lib/validation/expiry.ts
Agent:
Agent: Fixing validation logic...
```

### Agent Makes Fix

```
Agent: [Reads src/lib/validation/expiry.ts]
Agent:
Agent: Current code (line 15-17):
Agent: ```typescript
Agent: const month = parseInt(parts[0]);
Agent: if (month > 12) return false;
Agent: ```
Agent:
Agent: Issue: Doesn't check for month < 1, and should use >= instead of >
Agent:
Agent: [Updates src/lib/validation/expiry.ts]
Agent:
Agent: Fixed code:
Agent: ```typescript
Agent: const month = parseInt(parts[0]);
Agent: if (month < 1 || month > 12) return false;
Agent: ```
Agent:
Agent: Modified: src/lib/validation/expiry.ts
Agent: - Added check for month < 1
Agent: - Kept check for month > 12
Agent:
Agent: Re-running tests to verify fix...
```

### Tests Pass After Fix

```
Agent: $ npm test
Agent:
Agent: > payment-app@1.0.0 test
Agent: > jest
Agent:
Agent:  PASS  src/lib/validation/cardNumber.test.ts
Agent:  PASS  src/lib/validation/cvv.test.ts
Agent:  PASS  src/lib/validation/expiry.test.ts
Agent:    Credit Card Expiry Validation
Agent:      ✓ accepts valid future dates (15ms)
Agent:      ✓ rejects past dates (11ms)
Agent:      ✓ validates month range (18ms)
Agent:      ✓ handles edge case: December (14ms)
Agent:      ✓ rejects invalid format (12ms)
Agent:
Agent: Test Suites: 3 passed, 3 total
Agent: Tests:       7 passed, 7 total
Agent: Time:        3.245s
Agent:
Agent: ✓ All tests passed!
Agent:
Agent: Tests fixed successfully. Proceeding with commit...
```

### Successful Commit

```
Agent: Staging changes...
Agent: $ git add .
Agent:
Agent: Files staged:
Agent: - src/lib/validation/cardNumber.ts
Agent: - src/lib/validation/cardNumber.test.ts
Agent: - src/lib/validation/expiry.ts (includes fix)
Agent: - src/lib/validation/expiry.test.ts
Agent: - src/lib/validation/cvv.ts
Agent: - src/lib/validation/cvv.test.ts
Agent:
Agent: Cleaning up...
Agent: (No temporary files found)
Agent:
Agent: Creating commit...
Agent: $ git commit \
Agent:   -m "feat: implement credit card validation" \
Agent:   -m "- Add card number validation (Luhn algorithm)" \
Agent:   -m "- Add expiry date validation with month range check" \
Agent:   -m "- Add CVV validation (3-4 digits)" \
Agent:   -m "- Fix edge case: validate month is between 1-12" \
Agent:   -m "Completes Task 1.0 from PRD-payment-validation"
Agent:
Agent: [main 7b4c8d3] feat: implement credit card validation
Agent:  6 files changed, 287 insertions(+)
Agent:  create mode 100644 src/lib/validation/cardNumber.ts
Agent:  create mode 100644 src/lib/validation/cardNumber.test.ts
Agent:  create mode 100644 src/lib/validation/expiry.ts
Agent:  create mode 100644 src/lib/validation/expiry.test.ts
Agent:  create mode 100644 src/lib/validation/cvv.ts
Agent:  create mode 100644 src/lib/validation/cvv.test.ts
Agent:
Agent: ✓ Parent task 1.0 marked complete
Agent:
Agent: Progress: 3/5 sub-tasks, 1/2 parent tasks complete
Agent: Next task is 2.1: Validate amount range
Agent: Ready to proceed? (yes/y)
```

## What Happened

### 1. Tests Failed
- Agent detected 2 failing tests
- **Did NOT commit** (protecting code quality)
- Analyzed the failures

### 2. Agent Diagnosed Issue
- Read test expectations
- Identified root cause (month validation logic)
- Located the problematic code

### 3. Agent Fixed Issue
- Updated validation logic
- Fixed off-by-one error
- Added missing lower bound check

### 4. Verification
- Re-ran full test suite
- Confirmed all tests pass
- Only then proceeded with commit

### 5. Commit Included Fix
- Commit message noted the fix
- All related files included
- Clean, working state committed

## Alternative Scenario: Multiple Fix Attempts

Sometimes fixes require multiple iterations:

```
Agent: $ npm test
Agent: ✗ Tests failed (2 failures)
Agent:
Agent: Fixing...
Agent: [attempts fix #1]
Agent:
Agent: $ npm test
Agent: ✗ Tests failed (1 failure) - Progress!
Agent:
Agent: One test still failing. Analyzing...
Agent: [attempts fix #2]
Agent:
Agent: $ npm test
Agent: ✓ All tests passed!
Agent:
Agent: [proceeds with commit]
```

## Another Scenario: Agent Can't Fix Automatically

```
Agent: $ npm test
Agent: ✗ Tests failed (1 failure)
Agent:
Agent: Test failure in integration test:
Agent:   - PaymentGateway.test.ts: Connection timeout
Agent:
Agent: This appears to be an environment issue, not code issue.
Agent:
Agent: Attempted fix: Added retry logic
Agent: Re-running tests...
Agent:
Agent: $ npm test
Agent: ✗ Still failing with same error
Agent:
Agent: I cannot automatically fix this issue because:
Agent: - Appears to be external service dependency
Agent: - May require environment configuration
Agent: - Integration test, not unit test
Agent:
Agent: Recommendations:
Agent: 1. Check if payment gateway test server is running
Agent: 2. Verify API credentials in .env.test
Agent: 3. Check network connectivity
Agent: 4. Consider mocking external service for tests
Agent:
Agent: Would you like to:
Agent: a) Fix the issue manually and tell me to retry
Agent: b) Skip this test for now (not recommended)
Agent: c) Pause here and investigate
Agent:
Agent: Waiting for your decision...
```

**User:** `a - I'll fix it`

```
[User fixes the environment issue]

User: Issue fixed, retry tests

Agent: $ npm test
Agent: ✓ All tests passed!
Agent:
Agent: Great! Proceeding with commit...
```

## Key Benefits Demonstrated

### 1. **Quality Protection**
- **Never** commits broken code
- Tests must pass
- No exceptions

### 2. **Automatic Recovery**
- Attempts to fix test failures
- Re-runs tests to verify
- Multiple attempts if needed

### 3. **Transparency**
- Shows exact test output
- Explains what failed
- Describes fix attempts

### 4. **User Control**
- Agent can't fix everything
- Asks for help when stuck
- User can intervene anytime

### 5. **Clean History**
- Only working code committed
- Fixes included in same commit
- Professional commit messages

## Comparison: With vs Without Agent

### Without Agent (Manual Testing)

**Common mistakes:**
```bash
# Developer implements feature
git add .

# Oops, forgot to test!
git commit -m "add validation"

# Later...
npm test
# ✗ Tests fail!

# Now have to:
# 1. Fix the issue
# 2. Create another commit
# 3. Cluttered git history
```

**Git history:**
```
abc1234 add validation        ← broken code committed
def5678 fix validation bug    ← fix in separate commit
```

### With Agent (Automated Testing)

**Agent enforces quality:**
```bash
# Agent implements feature
# Agent runs tests automatically
# Tests fail
# Agent fixes issues
# Agent re-tests
# Only commits when tests pass
```

**Git history:**
```
abc1234 feat: implement validation  ← working code, fix included
```

Clean, professional, one commit.

## Real-World Impact

### Scenario: Team of 5 Developers

**Without Agent:**
- 2-3 broken commits per developer per week
- 10-15 total broken commits
- CI pipeline failures
- Frustrated team members
- Time wasted fixing issues
- Messy git history

**With Agent:**
- 0 broken commits
- CI always green
- Team confident in main branch
- Clean git history
- Time saved on fixes

## Summary

This example shows:

1. **Tests are mandatory** - No commits without passing tests
2. **Agent fixes failures** - Attempts automatic resolution
3. **Multiple attempts** - Keeps trying until tests pass
4. **User intervention** - Available when agent can't fix
5. **Quality first** - Never compromises on code quality

The agent acts as a **quality gatekeeper**, ensuring only working, tested code enters the repository.
