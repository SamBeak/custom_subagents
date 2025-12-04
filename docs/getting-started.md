# Getting Started

Welcome to the Custom Subagents repository! This guide will help you get up and running quickly.

## Prerequisites

- Basic understanding of Claude Code
- Familiarity with command line (Terminal/PowerShell)
- Text editor or IDE
- Git (for version control)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd custom_subagents
```

### 2. Explore the Structure

```bash
# View the repository structure
ls -la

# Check available categories
ls agents/
```

## Creating Your First Agent

### Using Windows (PowerShell)

1. Open PowerShell in the repository directory
2. Navigate to templates folder:
   ```powershell
   cd templates
   ```
3. Run the creation script:
   ```powershell
   .\create-agent.ps1
   ```
4. Follow the interactive prompts:
   - Enter agent name (e.g., `my-first-agent`)
   - Select category (1-6)
   - Provide description
   - Specify agent type
   - Enter your name as author

### Using Linux/Mac (Bash)

1. Open Terminal in the repository directory
2. Navigate to templates folder:
   ```bash
   cd templates
   ```
3. Make the script executable (first time only):
   ```bash
   chmod +x create-agent.sh
   ```
4. Run the creation script:
   ```bash
   ./create-agent.sh
   ```
5. Follow the interactive prompts

## Understanding Agent Structure

After creation, your agent will have this structure:

```
agents/[category]/[agent-name]/
├── agent.json          # Configuration and metadata
├── README.md           # Documentation
├── prompt.md           # System prompt
└── examples/           # Usage examples
    └── example1.md
```

### agent.json
Contains metadata and configuration:
- Agent name and description
- Available tools
- Capabilities
- Tags for categorization
- Example usage

### prompt.md
Defines the agent's behavior:
- Role and expertise
- Working process
- Quality guidelines
- Error handling
- Success criteria

### README.md
Documentation for users:
- Overview
- Capabilities
- Usage examples
- Input/output formats
- Best practices
- Limitations

## Customizing Your Agent

### Step 1: Edit the System Prompt

Open `prompt.md` and customize:

1. **Role**: What is the agent's primary function?
2. **Expertise**: What domains does it specialize in?
3. **Objectives**: What should it accomplish?
4. **Process**: How should it work step-by-step?
5. **Standards**: What quality standards should it follow?

Example:
```markdown
# My Custom Agent System Prompt

## Role
You are a specialized agent designed to analyze code quality and provide refactoring suggestions.

## Expertise
You have deep knowledge in:
- Clean code principles
- Design patterns
- Code smell detection
- Refactoring techniques
```

### Step 2: Configure Tools

Edit `agent.json` to specify which tools the agent can use:

```json
{
  "tools": [
    "Read",      // Read files
    "Write",     // Create new files
    "Edit",      // Modify existing files
    "Glob",      // Find files by pattern
    "Grep",      // Search content
    "Bash"       // Execute commands
  ]
}
```

**Common tool combinations:**

- **Analyzer agents**: Read, Glob, Grep
- **Generator agents**: Read, Write, Glob, Grep
- **Refactoring agents**: Read, Edit, Glob, Grep
- **Full-feature agents**: All tools

### Step 3: Write Documentation

Update `README.md` with:

1. **Clear overview**: What problem does this solve?
2. **Capabilities**: What can it do?
3. **Usage examples**: Show real-world use cases
4. **Best practices**: How to use it effectively
5. **Limitations**: What it cannot do

### Step 4: Add Examples

Create practical examples in the `examples/` folder:

```markdown
# Example 1: Basic Usage

## Input
User request: "Analyze this component for code smells"

## Process
1. Read the component file
2. Analyze code structure
3. Identify code smells
4. Provide refactoring suggestions

## Output
Generated report with:
- List of detected code smells
- Severity ratings
- Refactoring recommendations
```

## Testing Your Agent

### Manual Testing

1. Copy your agent to Claude Code's subagents directory
2. Configure it in Claude Code settings
3. Test with sample tasks
4. Verify outputs match expectations

### Validation

Run the validation script:

```bash
# From repository root
node scripts/validate-agents.js agents/category/your-agent
```

This checks:
- JSON syntax validity
- Required files present
- Metadata completeness
- Tool configuration

## Using Your Agent

### In Claude Code

Invoke using the Task tool:

```typescript
Task({
  subagent_type: "your-agent-name",
  prompt: "Detailed task description with all necessary context",
  description: "Brief 3-5 word task summary"
})
```

### Best Practices for Invocation

1. **Provide context**: Include all necessary information
2. **Be specific**: Clear task description
3. **Set expectations**: What output format you need
4. **Specify constraints**: Any limitations or requirements

## Next Steps

1. Read [Agent Development Guide](agent-development.md) for advanced techniques
2. Check [Best Practices](best-practices.md) for quality guidelines
3. Explore [Categories](categories.md) to understand agent organization
4. Review existing agents for inspiration

## Common First Steps

### 1. Explore Existing Agents
```bash
# View frontend agents
ls agents/frontend/

# Read an example agent
cat agents/frontend/example-agent/README.md
```

### 2. Create a Test Agent
Start with something simple:
- Category: documentation
- Type: analyzer
- Purpose: Extract TODO comments from code

### 3. Test and Iterate
- Create the agent
- Test with sample files
- Refine the prompt
- Update documentation
- Test again

## Troubleshooting

### Script won't run (PowerShell)
```powershell
# Set execution policy (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Script won't run (Bash)
```bash
# Make executable
chmod +x create-agent.sh
```

### Agent not recognized in Claude Code
1. Verify agent directory structure
2. Check agent.json syntax
3. Ensure all required files exist
4. Restart Claude Code

## Getting Help

- Check [Troubleshooting Guide](troubleshooting.md)
- Review [Agent Development Guide](agent-development.md)
- Look at existing agent examples
- Open an issue in the repository

## Summary

You've learned:
- How to create a new agent
- Understanding agent structure
- Customizing agent behavior
- Testing and validation
- Using agents in Claude Code

Ready to build your first agent? Follow the steps above and refer to other documentation as needed!
