# Agent Development Guide

This guide covers advanced topics for developing high-quality custom subagents.

## Table of Contents

1. [Design Principles](#design-principles)
2. [Prompt Engineering](#prompt-engineering)
3. [Tool Selection](#tool-selection)
4. [Agent Patterns](#agent-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Performance Optimization](#performance-optimization)
7. [Documentation Standards](#documentation-standards)

## Design Principles

### Single Responsibility Principle

Each agent should have one clear, focused purpose.

**Good Example:**
```
Agent: code-formatter
Purpose: Format code according to style guidelines
```

**Bad Example:**
```
Agent: code-helper
Purpose: Format, analyze, refactor, test, and document code
```

### Composability

Agents should work well with other agents and tools.

```markdown
## Working with Other Agents
This agent can be used in combination with:
- code-analyzer: First analyze, then refactor
- test-generator: Generate tests after refactoring
- documentation-writer: Document changes made
```

### Clear Boundaries

Define what the agent does and doesn't do.

```markdown
## Capabilities
- Analyzes JavaScript/TypeScript files
- Detects common code smells
- Suggests refactoring approaches

## Limitations
- Does not modify files automatically
- Does not generate tests
- Does not handle CSS/HTML analysis
```

## Prompt Engineering

### Structure Your Prompt

Use clear sections for different aspects:

```markdown
# Agent Name System Prompt

## Role
[Clear role definition]

## Expertise
[List of knowledge domains]

## Primary Objectives
1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

## Working Process
[Step-by-step approach]

## Output Standards
[Quality expectations]

## Error Handling
[How to handle issues]

## Constraints
[Limitations and boundaries]

## Success Criteria
[When is the task complete]
```

### Writing Effective Objectives

**Too vague:**
```
- Help users with their code
```

**Better:**
```
- Analyze code for SOLID principle violations
- Identify specific refactoring opportunities
- Provide actionable improvement suggestions with code examples
```

### Process Definition

Break down the working process into clear phases:

```markdown
## Working Process

### 1. Analysis Phase
- Read all relevant files using the Read tool
- Parse code structure and dependencies
- Identify patterns and anti-patterns
- Create analysis report

### 2. Evaluation Phase
- Rate severity of issues (Critical/High/Medium/Low)
- Prioritize based on impact
- Consider project context and constraints

### 3. Recommendation Phase
- Generate specific refactoring suggestions
- Provide code examples for each suggestion
- Explain benefits and trade-offs
- Estimate implementation effort

### 4. Documentation Phase
- Summarize findings
- Create actionable task list
- Link to relevant resources
```

### Quality Guidelines

Define specific quality criteria:

```markdown
## Output Standards

### Accuracy
- All code examples must be syntactically correct
- Suggestions must be applicable to the actual codebase
- Analysis must be based on current best practices

### Completeness
- Cover all files in the specified scope
- Address all relevant aspects of the code
- Include both immediate and long-term improvements

### Clarity
- Use clear, jargon-free language
- Provide examples for every suggestion
- Explain the "why" behind each recommendation
```

## Tool Selection

### Available Tools

Each tool has specific use cases:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| Read | Read file contents | Need to examine files |
| Write | Create new files | Generating new code/docs |
| Edit | Modify existing files | Making specific changes |
| Glob | Find files by pattern | Searching for file types |
| Grep | Search file contents | Finding specific code |
| Bash | Execute commands | Running tools, tests |

### Tool Combination Patterns

#### Analyzer Pattern
```json
{
  "tools": ["Read", "Glob", "Grep"]
}
```
Use for: Code analysis, documentation review, research tasks

#### Generator Pattern
```json
{
  "tools": ["Read", "Write", "Glob", "Grep"]
}
```
Use for: File generation, scaffolding, documentation creation

#### Refactoring Pattern
```json
{
  "tools": ["Read", "Edit", "Glob", "Grep"]
}
```
Use for: Code modifications, updates, refactoring

#### Full-Feature Pattern
```json
{
  "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
}
```
Use for: Complex tasks requiring all capabilities

### Tool Usage in Prompts

Guide the agent on tool usage:

```markdown
## Tool Usage Guidelines

### Read Tool
- ALWAYS read files before analyzing or modifying
- Read related files to understand context
- Read configuration files to understand project setup

### Glob Tool
- Use to find all files matching a pattern
- Helpful for discovering file structure
- Efficient for large codebases

### Grep Tool
- Search for specific patterns across files
- Useful for finding function/class definitions
- Helps identify dependencies

### Edit Tool
- ONLY use after reading the file
- Preserve existing formatting and style
- Make minimal, focused changes

### Write Tool
- For creating new files only
- Follow project conventions
- Include proper headers and documentation

### Bash Tool
- Run linters and formatters
- Execute tests to verify changes
- Install dependencies if needed
```

## Agent Patterns

### Pattern 1: Analyzer

**Purpose:** Examine code/documents and provide insights

**Structure:**
```markdown
## Working Process

1. **Discovery Phase**
   - Use Glob to find relevant files
   - Use Grep to locate specific patterns
   - Read files for detailed analysis

2. **Analysis Phase**
   - Parse and understand code structure
   - Identify patterns, anti-patterns, issues
   - Collect metrics and statistics

3. **Reporting Phase**
   - Generate structured report
   - Categorize findings
   - Prioritize recommendations
```

**Tools:** Read, Glob, Grep

### Pattern 2: Generator

**Purpose:** Create new files based on specifications

**Structure:**
```markdown
## Working Process

1. **Requirements Gathering**
   - Read specification files
   - Understand project structure
   - Identify dependencies

2. **Planning Phase**
   - Design file structure
   - Plan content organization
   - Determine naming conventions

3. **Generation Phase**
   - Create files using Write tool
   - Follow project conventions
   - Add necessary imports/dependencies

4. **Validation Phase**
   - Verify syntax correctness
   - Check against specifications
   - Ensure integration compatibility
```

**Tools:** Read, Write, Glob, Grep, Bash

### Pattern 3: Transformer

**Purpose:** Modify existing code/documents

**Structure:**
```markdown
## Working Process

1. **Analysis Phase**
   - Read target files
   - Understand current structure
   - Identify transformation requirements

2. **Planning Phase**
   - Plan modification strategy
   - Identify affected areas
   - Consider side effects

3. **Transformation Phase**
   - Use Edit tool for modifications
   - Maintain code style consistency
   - Preserve functionality

4. **Verification Phase**
   - Run tests if available
   - Verify syntax correctness
   - Check for regressions
```

**Tools:** Read, Edit, Glob, Grep, Bash

### Pattern 4: Orchestrator

**Purpose:** Coordinate multiple operations

**Structure:**
```markdown
## Working Process

1. **Task Breakdown**
   - Analyze overall requirement
   - Break into subtasks
   - Determine execution order

2. **Execution Phase**
   - Execute subtasks in sequence
   - Handle dependencies
   - Manage intermediate results

3. **Integration Phase**
   - Combine results
   - Ensure consistency
   - Verify completeness

4. **Finalization Phase**
   - Clean up temporary artifacts
   - Generate summary
   - Provide next steps
```

**Tools:** All tools (Read, Write, Edit, Glob, Grep, Bash)

## Testing Strategies

### Unit Testing

Test individual agent capabilities:

```markdown
# Test Case 1: File Discovery
**Input:** Codebase with 10 JavaScript files
**Expected:** Agent finds all 10 files
**Verification:** Count files in output

# Test Case 2: Pattern Detection
**Input:** File with 5 code smells
**Expected:** Agent detects all 5 issues
**Verification:** Compare with manual review

# Test Case 3: Recommendation Quality
**Input:** Component with prop-drilling
**Expected:** Suggests Context API or state management
**Verification:** Expert review of suggestions
```

### Integration Testing

Test agent in realistic scenarios:

```markdown
# Integration Test 1: Full Analysis Workflow
**Scenario:** Analyze a React component
**Steps:**
1. Agent receives component path
2. Reads component and dependencies
3. Analyzes code quality
4. Generates recommendations
**Verification:** Complete, accurate report produced

# Integration Test 2: Multi-file Refactoring
**Scenario:** Extract shared logic to utility
**Steps:**
1. Agent identifies duplicate code
2. Creates utility file
3. Updates source files
4. Verifies functionality
**Verification:** Tests pass, no regressions
```

### Edge Case Testing

```markdown
# Edge Case 1: Empty Files
**Input:** Empty JavaScript file
**Expected:** Graceful handling, skip or note

# Edge Case 2: Very Large Files
**Input:** 10,000 line file
**Expected:** Process without timeout, suggest splitting

# Edge Case 3: Syntax Errors
**Input:** File with syntax errors
**Expected:** Detect errors, suggest fixes, continue if possible
```

## Performance Optimization

### Minimize File Reads

```markdown
## Optimization: Batch File Reading

Instead of:
1. Read file1.js
2. Analyze file1.js
3. Read file2.js
4. Analyze file2.js

Do:
1. Glob to find all files
2. Read all necessary files
3. Analyze all files together
4. Generate combined report
```

### Use Efficient Search

```markdown
## Optimization: Search Before Read

Instead of:
- Read all files, then filter

Do:
- Grep to find relevant files
- Read only matched files
```

### Limit Scope

```markdown
## Define Clear Scope

In your prompt, specify:
- Maximum number of files to process
- Maximum file size to handle
- Depth of dependency analysis
- Timeout constraints

Example:
"Process up to 50 files, skip files larger than 5000 lines,
analyze direct dependencies only, timeout after 5 minutes"
```

## Documentation Standards

### README.md Template

```markdown
# Agent Name

## Overview
[1-2 sentence summary]

## Category
[Frontend/Backend/DevOps/Documentation/Business/Fullstack]

## Capabilities
- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]

## Usage

### Basic Example
[Simple, clear example]

### Advanced Example
[Complex use case]

## Input/Output Format

### Input
[What the agent expects]

### Output
[What the agent produces]

## Best Practices
1. [Practice 1]
2. [Practice 2]
3. [Practice 3]

## Limitations
- [Limitation 1]
- [Limitation 2]

## Version History
- v1.0.0: Initial release

## Author
[Your name]
```

### agent.json Best Practices

```json
{
  "name": "descriptive-agent-name",
  "type": "analyzer|generator|transformer|orchestrator",
  "description": "Clear, concise description of purpose",
  "category": "frontend|backend|devops|documentation|business|fullstack",
  "version": "1.0.0",
  "author": "Your Name",
  "tools": ["only", "necessary", "tools"],
  "capabilities": [
    "Specific capability 1",
    "Specific capability 2"
  ],
  "tags": ["relevant", "searchable", "tags"],
  "examples": [
    {
      "title": "Example 1 Title",
      "description": "What this example demonstrates",
      "input": "Sample input",
      "expectedOutput": "Expected result"
    }
  ]
}
```

### Example Documentation

Create comprehensive examples:

```markdown
# Example 1: Analyzing a React Component

## Context
Large React component with multiple responsibilities

## Input
Path to component: `src/components/UserDashboard.jsx`

## Agent Process
1. Reads the component file
2. Identifies separate concerns:
   - Data fetching
   - State management
   - UI rendering
3. Analyzes complexity metrics
4. Generates refactoring plan

## Output
\`\`\`markdown
# UserDashboard Analysis Report

## Issues Detected
1. Component too large (500 lines)
2. Multiple responsibilities (SRP violation)
3. Complex state management

## Recommendations
1. Extract data fetching to custom hook
2. Split UI into smaller components
3. Consider state management library

## Proposed Structure
- UserDashboard.jsx (main component)
- useUserData.js (custom hook)
- UserProfile.jsx (sub-component)
- UserStats.jsx (sub-component)
\`\`\`

## Next Steps
1. Review recommendations
2. Approve refactoring plan
3. Execute refactoring
4. Run tests
```

## Version Management

### Semantic Versioning

- **Major (1.0.0 → 2.0.0)**: Breaking changes to agent behavior
- **Minor (1.0.0 → 1.1.0)**: New features, backward compatible
- **Patch (1.0.0 → 1.0.1)**: Bug fixes, minor improvements

### Changelog

Maintain a version history:

```markdown
## Version History

### v1.2.0 (2025-01-25)
- Added support for TypeScript analysis
- Improved performance for large files
- Enhanced error messages

### v1.1.0 (2025-01-20)
- Added JSX/TSX support
- New metric: cyclomatic complexity
- Better handling of edge cases

### v1.0.0 (2025-01-15)
- Initial release
- Basic JavaScript analysis
- Code smell detection
```

## Summary

Key takeaways:
1. Follow single responsibility principle
2. Write clear, structured prompts
3. Choose appropriate tools
4. Use established patterns
5. Test thoroughly
6. Document comprehensively
7. Version properly

For more information, see:
- [Getting Started Guide](getting-started.md)
- [Best Practices](best-practices.md)
- [Troubleshooting](troubleshooting.md)
