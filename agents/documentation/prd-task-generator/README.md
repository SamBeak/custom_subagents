# PRD Task Generator

## Overview
A specialized agent that analyzes Product Requirements Documents (PRD) and generates comprehensive, hierarchical task lists in Markdown format. Designed to help developers systematically implement features by breaking down requirements into actionable steps.

## Category
documentation

## Capabilities
- Analyze PRD functional requirements and user stories
- Assess current codebase state and identify existing components
- Generate hierarchical task lists (parent tasks and sub-tasks)
- Identify relevant files that need creation or modification
- Create structured Markdown task documentation
- Interactive task generation with user confirmation

## Tools Available
- **Read**: Load and analyze PRD files and codebase
- **Write**: Create task list Markdown files
- **Glob**: Find existing files and understand project structure
- **Grep**: Search for specific patterns and components in codebase

## Usage

### Basic Example

```
Task with subagent_type: prd-task-generator
Prompt: "Generate implementation tasks from /docs/prd-user-profile-editing.md"
```

**Agent Response:**
1. Analyzes the PRD
2. Assesses current codebase
3. Generates high-level parent tasks
4. Waits for your "Go" confirmation
5. Generates detailed sub-tasks
6. Saves task list to `/tasks/tasks-prd-user-profile-editing.md`

### Advanced Example

```
Task with subagent_type: prd-task-generator
Prompt: "Create implementation plan from /docs/prd-dashboard-redesign.md. Focus on identifying reusable components from the existing design system."
```

The agent will:
- Read the PRD
- Scan the codebase for existing design system components
- Generate tasks that leverage existing components
- Create new tasks only for missing functionality
- Provide file paths for both new and modified components

## Interactive Workflow

This agent uses a two-phase approach:

### Phase 1: High-Level Planning
1. Agent analyzes PRD and codebase
2. Generates parent tasks (3-7 high-level tasks)
3. Presents tasks to you
4. **Waits for confirmation** - Agent will pause here
5. You review and respond with "Go" to proceed

### Phase 2: Detailed Planning
6. Agent generates sub-tasks for each parent task
7. Identifies all relevant files
8. Saves complete task list

This ensures alignment before detailed planning.

## Input/Output Format

### Input
- **PRD File Path**: Path to the Product Requirements Document
- **Optional Context**: Additional guidance (e.g., "focus on backend tasks", "reuse existing auth system")

**Example Input:**
```
Generate tasks from /docs/prd-user-authentication.md
```

### Output
A Markdown file saved to `/tasks/tasks-[prd-name].md` with this structure:

```markdown
## Relevant Files

- `src/components/LoginForm.tsx` - Main login component
- `src/components/LoginForm.test.tsx` - Unit tests for LoginForm
- `src/lib/auth/authService.ts` - Authentication service logic
- `src/lib/auth/authService.test.ts` - Tests for auth service
- `src/app/api/auth/route.ts` - API route for authentication

### Notes

- Unit tests should be placed alongside code files
- Run tests with: `npx jest [optional/path/to/test/file]`
- Follow existing authentication patterns in codebase

## Tasks

- [ ] 1.0 Set up authentication infrastructure
  - [ ] 1.1 Create authentication service with login/logout methods
  - [ ] 1.2 Implement JWT token generation and validation
  - [ ] 1.3 Set up secure session storage
  - [ ] 1.4 Add authentication middleware for protected routes

- [ ] 2.0 Build login UI component
  - [ ] 2.1 Create LoginForm component with email/password inputs
  - [ ] 2.2 Add form validation (email format, password requirements)
  - [ ] 2.3 Implement error handling and user feedback
  - [ ] 2.4 Add "Forgot Password" link and flow

- [ ] 3.0 Implement API endpoints
  - [ ] 3.1 Create POST /api/auth/login endpoint
  - [ ] 3.2 Create POST /api/auth/logout endpoint
  - [ ] 3.3 Add rate limiting to prevent brute force attacks
  - [ ] 3.4 Implement proper error responses

- [ ] 4.0 Add testing and documentation
  - [ ] 4.1 Write unit tests for authentication service
  - [ ] 4.2 Write component tests for LoginForm
  - [ ] 4.3 Write integration tests for auth flow
  - [ ] 4.4 Document authentication setup in README
```

## Best Practices

### 1. Provide Clear PRD Path
```
Good: Generate tasks from /docs/prd-user-profile.md
Avoid: Generate tasks from the user profile PRD
```

### 2. Include Context When Helpful
```
Generate tasks from /docs/prd-payment.md
Context: We already have Stripe integration, focus on UI and flow
```

### 3. Review Parent Tasks Before Proceeding
- Check that high-level tasks make sense
- Ensure nothing is missing
- Verify task order is logical
- Respond with "Go" only when satisfied

### 4. Use Generated Tasks as Living Documents
- Check off tasks as completed
- Add notes or issues discovered during implementation
- Update if requirements change

### 5. Leverage Codebase Assessment
- Agent will identify existing components to reuse
- Trust the file paths provided (based on codebase scan)
- Review "Relevant Files" section for modification candidates

## Limitations

### What This Agent Does
- ✅ Analyzes PRD requirements
- ✅ Generates hierarchical task lists
- ✅ Identifies relevant files in codebase
- ✅ Creates structured Markdown documentation
- ✅ Provides interactive validation

### What This Agent Does NOT Do
- ❌ Implement the code (only plans it)
- ❌ Modify PRD documents
- ❌ Execute tasks automatically
- ❌ Estimate time/effort for tasks
- ❌ Assign tasks to team members
- ❌ Track task completion status

### Technical Limitations
- Works best with well-structured PRDs
- Requires accessible codebase for assessment
- Cannot access external dependencies or documentation
- File path accuracy depends on project structure consistency

## Common Use Cases

### Use Case 1: New Feature Implementation
**Scenario:** Product team provides PRD for new feature
**Action:** Generate comprehensive task list
**Benefit:** Clear roadmap for development team

### Use Case 2: Feature Refinement
**Scenario:** Existing feature needs updates per new PRD
**Action:** Generate tasks that identify modification points
**Benefit:** Minimize unnecessary changes, leverage existing code

### Use Case 3: Onboarding New Developers
**Scenario:** Junior developer assigned to implement feature
**Action:** Generate detailed, step-by-step task list
**Benefit:** Clear guidance with context about existing codebase

### Use Case 4: Sprint Planning
**Scenario:** Need to break down feature into sprint-sized tasks
**Action:** Generate tasks, use parent tasks as sprint milestones
**Benefit:** Clear sprint goals and deliverables

## Troubleshooting

### Agent Can't Find PRD
**Problem:** Error reading PRD file
**Solution:**
- Verify file path is correct (use absolute or relative to project root)
- Check file exists: `ls /docs/prd-*.md`
- Ensure file is readable Markdown format

### Generated Tasks Too Generic
**Problem:** Tasks lack specific details
**Solution:**
- Provide more detailed PRD
- Add context in your prompt
- After parent tasks, suggest refinements before "Go"

### Missing Relevant Files
**Problem:** Agent doesn't identify key files
**Solution:**
- Ensure files follow standard naming conventions
- Add context: "Include files in /legacy folder"
- Manually review and add missing files to task list

### Tasks Don't Match Codebase Patterns
**Problem:** Generated tasks ignore existing architecture
**Solution:**
- Ensure codebase is accessible
- Add context: "Follow existing pattern in /src/features"
- Review parent tasks and provide guidance before "Go"

### Output File Not Created
**Problem:** Task list not saved
**Solution:**
- Ensure `/tasks` directory exists (create if needed)
- Check write permissions
- Agent will display content if save fails - copy manually

## Example Session

```
User: Generate tasks from /docs/prd-user-settings.md

Agent: [Analyzes PRD and codebase...]

I have generated the high-level tasks based on the PRD:

- [ ] 1.0 Create user settings data model and API
- [ ] 2.0 Build settings UI components
- [ ] 3.0 Implement settings persistence and synchronization
- [ ] 4.0 Add settings validation and error handling
- [ ] 5.0 Write tests and documentation

Ready to generate the sub-tasks? Respond with 'Go' to proceed.

User: Go

Agent: [Generates detailed sub-tasks, identifies files, saves document...]

✅ Task list generated and saved to: /tasks/tasks-prd-user-settings.md

Summary:
- 5 parent tasks
- 23 sub-tasks
- 12 relevant files identified (8 new, 4 modifications)
```

## Integration with Development Workflow

### Recommended Workflow

1. **Product writes PRD** → Save to `/docs/prd-[feature].md`
2. **Invoke this agent** → Generate task list
3. **Review parent tasks** → Validate approach
4. **Confirm with "Go"** → Get detailed sub-tasks
5. **Review task list** → Adjust if needed
6. **Begin implementation** → Check off tasks as completed
7. **Update as needed** → Modify tasks if requirements change

### Works Well With

- **Version Control**: Track task list changes alongside code
- **Project Management**: Import tasks into Jira, Linear, etc.
- **Code Review**: Reference task numbers in PRs
- **Documentation**: Link to generated tasks from main docs

## Version History

### v1.0.0
- Initial release
- PRD analysis and task generation
- Interactive two-phase workflow
- Codebase assessment
- Hierarchical task structure
- Relevant files identification

## Author
Custom Subagents Repository

---

**Need help?** Check the [Troubleshooting Guide](../../../docs/troubleshooting.md) or open an issue.
