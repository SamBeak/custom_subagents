# Custom Subagents Repository

A comprehensive collection of custom subagents for Claude Code, organized by category and purpose.

## Overview

This repository contains specialized subagents designed to enhance Claude Code's capabilities across various domains including frontend development, backend services, DevOps automation, documentation, and business analysis.

## Repository Structure

```
custom_subagents/
├── agents/                      # All custom agents organized by category
│   ├── frontend/               # Frontend-related agents
│   ├── backend/                # Backend-related agents
│   ├── devops/                 # DevOps and infrastructure agents
│   ├── documentation/          # Documentation generation agents
│   ├── business/               # Business analysis and planning agents
│   └── fullstack/              # Full-stack development agents
│
├── templates/                   # Templates for creating new agents
│   ├── agent-template/         # Base template files
│   ├── create-agent.sh         # Linux/Mac creation script
│   └── create-agent.ps1        # Windows creation script
│
├── docs/                        # Documentation
│   ├── getting-started.md      # Getting started guide
│   ├── agent-development.md    # Agent development guide
│   ├── best-practices.md       # Best practices
│   ├── categories.md           # Category descriptions
│   └── troubleshooting.md      # Common issues and solutions
│
├── scripts/                     # Utility scripts
│   ├── validate-agents.js      # Agent validation
│   ├── test-agent.js           # Agent testing
│   └── export-for-claude.js    # Export for Claude Code
│
└── tests/                       # Test suites
    ├── agent-tests/
    └── integration-tests/
```

## Categories

### Frontend
Agents specialized in frontend development, UI/UX generation, and client-side technologies.

**Examples:**
- `jsp-generator-from-image`: Generate JSP files from UI screenshots
- `html-generator-from-image`: Generate HTML/Thymeleaf from UI screenshots
- `figma-prompt-generator`: Generate Figma Make prompts from design documents

### Backend
Agents focused on server-side development, API design, and backend architecture.

### DevOps
Agents for infrastructure automation, CI/CD, deployment, and operations.

### Documentation
Agents specialized in generating and analyzing technical documentation.

**Examples:**
- `rfp-analyzer`: Analyze RFP documents for Korean government projects
- `rfp-respondent`: Generate responses to RFP requirements
- `trd-generator`: Generate Technical Requirements Documents

### Business
Agents for business analysis, project planning, and strategic documentation.

**Examples:**
- `promotion-strategy`: Generate strategic frameworks for projects
- `project-analyzer`: Extract key information from project briefings
- `process-image-promptor`: Generate prompts for business process diagrams

### Fullstack
Agents that span both frontend and backend development.

## Quick Start

### Creating a New Agent

#### On Windows (PowerShell)
```powershell
cd templates
.\create-agent.ps1
```

#### On Linux/Mac (Bash)
```bash
cd templates
chmod +x create-agent.sh
./create-agent.sh
```

The script will guide you through:
1. Entering agent name
2. Selecting category
3. Providing description
4. Specifying agent type
5. Adding author information

### Agent Structure

Each agent follows a standardized structure:

```
agent-name/
├── agent.json          # Agent configuration and metadata
├── README.md           # Agent documentation
├── prompt.md           # System prompt defining agent behavior
└── examples/           # Usage examples
    └── example1.md
```

## Using Agents with Claude Code

1. **Copy agent directory** to your Claude Code subagents folder
2. **Configure** the agent in your Claude Code settings
3. **Invoke** using the Task tool with appropriate subagent_type

Example:
```typescript
Task({
  subagent_type: "your-agent-name",
  prompt: "Your task description",
  description: "Brief task description"
})
```

## Development Guidelines

### Agent Configuration (`agent.json`)
- Define available tools
- Specify capabilities
- Add relevant tags
- Include usage examples

### System Prompt (`prompt.md`)
- Clear role definition
- Detailed expertise areas
- Step-by-step working process
- Quality guidelines
- Error handling procedures

### Documentation (`README.md`)
- Overview and purpose
- Capabilities list
- Usage examples
- Input/output formats
- Best practices
- Limitations

## Best Practices

1. **Single Responsibility**: Each agent should have a focused, well-defined purpose
2. **Clear Documentation**: Comprehensive README and examples
3. **Consistent Structure**: Follow the template structure
4. **Quality Prompts**: Write detailed, unambiguous system prompts
5. **Tool Selection**: Only include necessary tools in agent.json
6. **Version Control**: Use semantic versioning for agent updates
7. **Testing**: Test agents thoroughly before deployment

## Contributing

### Adding a New Agent
1. Use the creation scripts to generate base structure
2. Customize prompt.md for agent behavior
3. Update README.md with comprehensive documentation
4. Add practical examples
5. Test thoroughly
6. Submit pull request

### Updating Existing Agents
1. Follow semantic versioning
2. Document changes in README.md
3. Update version in agent.json
4. Test compatibility

## Validation

Validate your agent configuration:
```bash
node scripts/validate-agents.js agents/category/your-agent
```

## Testing

Test your agent:
```bash
node scripts/test-agent.js agents/category/your-agent
```

## Resources

- [Getting Started Guide](docs/getting-started.md)
- [Agent Development Guide](docs/agent-development.md)
- [Best Practices](docs/best-practices.md)
- [Category Guide](docs/categories.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions:
- Open an issue in the repository
- Submit a pull request
- Check documentation in `/docs`

## Changelog

### v1.0.0 (2025-01-25)
- Initial repository structure
- Cross-platform agent creation scripts
- Template system for new agents
- Category-based organization
- Comprehensive documentation

---

**Happy Building!** 🚀
