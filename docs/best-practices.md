# Best Practices for Custom Subagents

This guide outlines best practices for creating, maintaining, and using custom subagents effectively.

## Table of Contents

1. [Agent Design](#agent-design)
2. [Prompt Writing](#prompt-writing)
3. [Configuration](#configuration)
4. [Documentation](#documentation)
5. [Testing](#testing)
6. [Maintenance](#maintenance)
7. [Usage](#usage)

## Agent Design

### Do: Focus on Single Responsibility

Each agent should excel at one specific task.

**Good:**
```
agent: react-component-analyzer
Purpose: Analyze React components for best practices and anti-patterns
```

**Avoid:**
```
agent: web-development-helper
Purpose: Do everything web-related
```

### Do: Make Agents Composable

Design agents that work well together.

```
Workflow Example:
1. code-analyzer → Identifies issues
2. refactoring-agent → Implements fixes
3. test-generator → Creates tests
4. documentation-writer → Documents changes
```

### Do: Define Clear Boundaries

**Example:**
```markdown
## What This Agent Does
- Analyzes JavaScript/TypeScript files
- Detects code smells and anti-patterns
- Suggests specific refactoring strategies

## What This Agent Does NOT Do
- Does not modify code automatically
- Does not generate tests
- Does not handle CSS/HTML
- Does not deploy changes
```

### Don't: Create Overly Generic Agents

**Avoid:**
```
agent: code-helper
Description: Helps with code
```

**Instead:**
```
agent: typescript-interface-generator
Description: Generates TypeScript interfaces from JSON schemas
```

### Do: Consider the User's Workflow

Design agents that fit into natural workflows:

```markdown
## Typical Usage Flow

1. Developer writes code
2. Runs code-analyzer agent
3. Reviews recommendations
4. Invokes refactoring-agent for specific fixes
5. Runs tests
6. Commits changes
```

## Prompt Writing

### Do: Use Clear Structure

```markdown
# Agent Name System Prompt

## Role
[One sentence role definition]

## Expertise
- [Specific expertise area 1]
- [Specific expertise area 2]
- [Specific expertise area 3]

## Primary Objectives
1. [Clear objective 1]
2. [Clear objective 2]
3. [Clear objective 3]

## Working Process
[Detailed step-by-step process]

## Output Standards
[Specific quality criteria]
```

### Do: Be Specific About Process

**Good:**
```markdown
## Working Process

1. **File Discovery Phase**
   - Use Glob tool to find all .jsx and .tsx files
   - Filter out node_modules and build directories
   - Create list of files to analyze

2. **Analysis Phase**
   - Read each file using Read tool
   - Parse component structure
   - Check for common anti-patterns:
     * Prop drilling (more than 3 levels)
     * Large components (>300 lines)
     * Missing key props in lists
     * Inline function definitions in render
```

**Avoid:**
```markdown
## Working Process
1. Find files
2. Analyze them
3. Report results
```

### Do: Define Output Format

```markdown
## Output Format

Generate a markdown report with:

1. **Executive Summary**
   - Total files analyzed
   - Issues found by severity
   - Overall code quality score

2. **Detailed Findings**
   For each issue:
   - File path and line number
   - Issue description
   - Severity (Critical/High/Medium/Low)
   - Recommendation
   - Code example

3. **Prioritized Action Items**
   - Top 5 issues to address first
   - Estimated effort for each
```

### Do: Include Error Handling

```markdown
## Error Handling

If you encounter:

**Syntax Errors**
- Note the error location
- Continue analyzing other files
- Include errors in final report

**Permission Issues**
- Log the inaccessible file
- Continue with accessible files
- Report skipped files

**Large Files (>5000 lines)**
- Analyze first 1000 lines for quick wins
- Suggest file splitting as primary recommendation
- Note incomplete analysis in report
```

### Don't: Use Ambiguous Instructions

**Avoid:**
```markdown
Analyze the code and make it better.
```

**Instead:**
```markdown
Analyze the code for:
1. SOLID principle violations
2. Common design pattern opportunities
3. Performance bottlenecks
4. Security vulnerabilities

For each finding, provide:
- Specific line numbers
- Explanation of the issue
- Concrete refactoring suggestion
- Code example of the fix
```

## Configuration

### Do: Minimize Tool Selection

Only include necessary tools:

```json
{
  "tools": ["Read", "Glob", "Grep"]
}
```

Don't include tools the agent won't use:

```json
{
  "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
}
```
(Only if ALL tools are actually needed)

### Do: Use Descriptive Metadata

```json
{
  "name": "react-hook-analyzer",
  "type": "analyzer",
  "description": "Analyzes React hooks for proper usage patterns and detects common mistakes",
  "category": "frontend",
  "version": "1.2.0",
  "author": "Your Name"
}
```

### Do: Add Relevant Tags

```json
{
  "tags": [
    "react",
    "hooks",
    "analysis",
    "best-practices",
    "javascript",
    "typescript"
  ]
}
```

### Do: Include Practical Examples

```json
{
  "examples": [
    {
      "title": "Analyzing a Custom Hook",
      "description": "Detect issues in a useAuth hook",
      "input": "Analyze src/hooks/useAuth.js",
      "expectedOutput": "Report identifying missing dependency in useEffect"
    }
  ]
}
```

## Documentation

### Do: Write for Your Audience

**For end users:**
```markdown
# Quick Start

To analyze your React components:

1. Invoke the agent with your component path
2. Review the generated report
3. Address high-priority issues first
4. Re-run to verify improvements
```

**For developers:**
```markdown
# Implementation Details

This agent uses:
- ESLint rules for static analysis
- Abstract Syntax Tree (AST) parsing
- Pattern matching for anti-pattern detection
- Metrics calculation for complexity
```

### Do: Provide Complete Examples

```markdown
# Example: Analyzing a Component

## Input
\`\`\`
Analyze src/components/UserProfile.jsx
\`\`\`

## Agent Actions
1. Reads UserProfile.jsx
2. Parses component structure
3. Analyzes for issues
4. Generates report

## Output
\`\`\`markdown
# Analysis Report: UserProfile.jsx

## Summary
- Lines of code: 245
- Issues found: 4 (1 High, 3 Medium)
- Complexity score: 7/10

## High Priority Issues

### 1. Prop Drilling (Line 45-78)
**Issue:** Props passed through 4 component levels
**Impact:** Maintenance difficulty, tight coupling
**Recommendation:** Use Context API or state management

**Current Code:**
\`\`\`jsx
<ParentComponent user={user}>
  <MiddleComponent user={user}>
    <ChildComponent user={user} />
  </MiddleComponent>
</ParentComponent>
\`\`\`

**Suggested Fix:**
\`\`\`jsx
// Create context
const UserContext = createContext();

// Provider in parent
<UserContext.Provider value={user}>
  <ParentComponent>
    <MiddleComponent>
      <ChildComponent />
    </MiddleComponent>
  </ParentComponent>
</UserContext.Provider>

// Use in child
const ChildComponent = () => {
  const user = useContext(UserContext);
  // ...
};
\`\`\`
\`\`\`
```

### Do: Document Limitations

```markdown
## Limitations

**File Types**
- Only analyzes .js, .jsx, .ts, .tsx files
- Does not process .vue or .svelte files

**Analysis Depth**
- Analyzes direct dependencies only
- Does not follow npm package internals
- Maximum 100 files per run

**Detection Capabilities**
- Detects common patterns only
- May miss project-specific anti-patterns
- Requires manual review for context
```

### Don't: Assume Prior Knowledge

**Avoid:**
```markdown
Use the agent to analyze your components.
```

**Instead:**
```markdown
## How to Use

1. **Locate your component file**
   Example: `src/components/Dashboard.jsx`

2. **Invoke the agent**
   In Claude Code, use:
   \`\`\`
   Task with subagent_type: react-component-analyzer
   Prompt: "Analyze src/components/Dashboard.jsx"
   \`\`\`

3. **Review the report**
   The agent will generate a detailed analysis with:
   - Issue descriptions
   - Code examples
   - Refactoring suggestions

4. **Address issues**
   Start with high-priority items
   Test after each change
```

## Testing

### Do: Test Edge Cases

```markdown
# Test Cases

## Normal Cases
- Single component file ✓
- Multiple component files ✓
- TypeScript components ✓

## Edge Cases
- Empty files → Should skip gracefully
- Very large files (>5000 lines) → Should handle with warnings
- Syntax errors → Should continue with other files
- No issues found → Should report "No issues detected"

## Error Cases
- File not found → Should provide clear error message
- Invalid file type → Should skip with warning
- Permission denied → Should log and continue
```

### Do: Validate Output Quality

```markdown
# Quality Checks

For each test:
1. Output is valid markdown
2. All code examples are syntactically correct
3. File paths are accurate
4. Line numbers are correct
5. Recommendations are actionable
6. No false positives
7. No missed obvious issues
```

### Do: Test with Real Code

Don't just test with simple examples. Use real-world code:

```markdown
# Real-World Test Cases

1. **Large Production Component**
   - 500+ lines
   - Multiple state hooks
   - Complex logic
   - Expected: Identifies real issues

2. **Well-Written Component**
   - Follows best practices
   - Clean code
   - Expected: Minimal or no issues

3. **Legacy Component**
   - Old patterns
   - Class components
   - Expected: Suggests modern patterns
```

## Maintenance

### Do: Version Semantically

```
1.0.0 → Initial release
1.1.0 → Add TypeScript support (new feature)
1.1.1 → Fix regex parsing bug (bug fix)
2.0.0 → Change output format (breaking change)
```

### Do: Maintain Changelog

```markdown
# Changelog

## [1.2.0] - 2025-01-25
### Added
- Support for analyzing custom hooks
- Detection of missing dependency arrays

### Changed
- Improved performance for large files

### Fixed
- False positive for useCallback dependencies

## [1.1.0] - 2025-01-20
### Added
- TypeScript support
- JSX/TSX file analysis

## [1.0.0] - 2025-01-15
### Added
- Initial release
- Basic React component analysis
```

### Do: Gather Feedback

```markdown
# Feedback Collection

Track:
- False positives
- Missed issues
- Confusing recommendations
- Performance problems
- Feature requests

Use this to:
- Improve detection accuracy
- Refine recommendations
- Add new capabilities
- Fix bugs
```

## Usage

### Do: Provide Context

**Good invocation:**
```
Analyze src/components/UserDashboard.jsx

Context:
- Part of a React 18 application
- Uses Redux for state management
- Follow company style guide (camelCase, functional components)
- Target: Improve performance and maintainability
```

**Weak invocation:**
```
Analyze the file
```

### Do: Be Specific About Needs

**Good:**
```
Analyze src/components/UserDashboard.jsx

Focus on:
1. Performance optimization opportunities
2. Accessibility issues
3. State management patterns

Output format: Prioritized list with code examples
```

**Weak:**
```
Make the code better
```

### Do: Iterate and Refine

```markdown
# Workflow

1. **Initial Analysis**
   Run agent → Review results

2. **Clarify**
   If unclear → Ask agent for details on specific findings

3. **Implement**
   Fix high-priority issues

4. **Verify**
   Re-run agent → Confirm improvements

5. **Iterate**
   Address remaining issues
```

### Don't: Ignore Agent Recommendations

Review all recommendations carefully:
- Understand the reasoning
- Consider the context
- Make informed decisions
- Document why you might skip certain suggestions

## Summary Checklist

### Agent Creation
- [ ] Focused, single-purpose design
- [ ] Clear boundaries defined
- [ ] Appropriate tool selection
- [ ] Comprehensive documentation

### Prompt Quality
- [ ] Clear structure
- [ ] Specific process steps
- [ ] Defined output format
- [ ] Error handling included

### Configuration
- [ ] Minimal tool set
- [ ] Descriptive metadata
- [ ] Relevant tags
- [ ] Practical examples

### Documentation
- [ ] Clear usage instructions
- [ ] Complete examples
- [ ] Documented limitations
- [ ] No assumed knowledge

### Testing
- [ ] Edge cases covered
- [ ] Output validated
- [ ] Real-world testing
- [ ] Quality checks passed

### Maintenance
- [ ] Semantic versioning
- [ ] Changelog maintained
- [ ] Feedback collected
- [ ] Regular updates

### Usage
- [ ] Context provided
- [ ] Specific needs stated
- [ ] Iterative refinement
- [ ] Recommendations reviewed

Follow these practices to create effective, maintainable, and user-friendly custom subagents!
