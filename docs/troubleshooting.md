# Troubleshooting Guide

Common issues and solutions for working with custom subagents.

## Table of Contents

1. [Creation Issues](#creation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Runtime Issues](#runtime-issues)
4. [Integration Issues](#integration-issues)
5. [Performance Issues](#performance-issues)
6. [Documentation Issues](#documentation-issues)

## Creation Issues

### Script Won't Execute (PowerShell)

**Problem:** `create-agent.ps1` shows execution policy error

**Error Message:**
```
File cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run script directly
PowerShell -ExecutionPolicy Bypass -File .\create-agent.ps1
```

**Alternative:**
```powershell
# Right-click create-agent.ps1 → Properties → Unblock
# Then run normally
.\create-agent.ps1
```

---

### Script Won't Execute (Bash)

**Problem:** `create-agent.sh` permission denied

**Error Message:**
```
bash: ./create-agent.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x create-agent.sh

# Run script
./create-agent.sh
```

**Alternative:**
```bash
# Run with bash directly
bash create-agent.sh
```

---

### Invalid Category Selection

**Problem:** Script fails after selecting category

**Error Message:**
```
Error: Invalid category selection
```

**Solution:**
1. Ensure you enter a number (1-6)
2. Don't enter category name directly
3. Check for typos

**Correct:**
```
Select category: 1
```

**Incorrect:**
```
Select category: frontend
```

---

### Template Files Not Found

**Problem:** Script can't find template files

**Error Message:**
```
Error: Template file not found
```

**Solution:**
```bash
# Ensure you're in the templates directory
cd templates

# Or run from repository root
cd ..
./templates/create-agent.sh  # Linux/Mac
.\templates\create-agent.ps1  # Windows
```

**Verify templates exist:**
```bash
ls -la templates/agent-template/
```

## Configuration Issues

### Invalid JSON in agent.json

**Problem:** Agent configuration won't parse

**Error Message:**
```
SyntaxError: Unexpected token in JSON
```

**Solution:**
1. Validate JSON syntax
2. Check for:
   - Missing commas
   - Trailing commas
   - Unescaped quotes
   - Missing brackets/braces

**Validate:**
```bash
# Using Node.js
node -e "console.log(JSON.parse(require('fs').readFileSync('agent.json')))"

# Using Python
python -m json.tool agent.json

# Online: jsonlint.com
```

**Common errors:**
```json
{
  "name": "test-agent",
  "tools": ["Read", "Write",]  ❌ Trailing comma
}
```

```json
{
  "name": "test-agent"
  "tools": ["Read"]  ❌ Missing comma
}
```

---

### Missing Required Fields

**Problem:** Agent configuration incomplete

**Error Message:**
```
Error: Missing required field 'description'
```

**Solution:**
Ensure agent.json includes all required fields:
```json
{
  "name": "required",
  "type": "required",
  "description": "required",
  "category": "required",
  "version": "required",
  "author": "required",
  "tools": ["required"],
  "capabilities": ["required"],
  "tags": ["optional"],
  "examples": ["optional"]
}
```

---

### Invalid Tool Names

**Problem:** Agent specifies non-existent tools

**Error Message:**
```
Error: Unknown tool 'Execute'
```

**Solution:**
Use only valid tool names:
- Read
- Write
- Edit
- Glob
- Grep
- Bash

**Incorrect:**
```json
{
  "tools": ["Execute", "Run", "Search"]
}
```

**Correct:**
```json
{
  "tools": ["Bash", "Grep"]
}
```

## Runtime Issues

### Agent Not Recognized

**Problem:** Claude Code doesn't see the agent

**Symptoms:**
- Agent not in subagent list
- "Unknown subagent" error

**Solution:**

1. **Check agent location:**
   ```
   agents/[category]/[agent-name]/
   ├── agent.json
   ├── README.md
   ├── prompt.md
   └── examples/
   ```

2. **Verify agent.json:**
   ```bash
   cat agents/frontend/my-agent/agent.json
   ```

3. **Restart Claude Code:**
   - Close all Claude Code instances
   - Restart application
   - Check subagent list again

4. **Check naming:**
   - Use kebab-case: `my-agent` ✓
   - Not camelCase: `myAgent` ✗
   - Not spaces: `my agent` ✗

---

### Agent Fails to Start

**Problem:** Agent throws error on invocation

**Error Message:**
```
Error: Failed to initialize agent
```

**Solution:**

1. **Check prompt.md exists:**
   ```bash
   ls agents/category/agent-name/prompt.md
   ```

2. **Validate prompt.md format:**
   - Must be valid markdown
   - No special characters that break parsing
   - Proper encoding (UTF-8)

3. **Check for syntax errors in prompt:**
   ```markdown
   # Valid Prompt

   ## Role
   You are an agent...

   ## Expertise
   - Item 1
   - Item 2
   ```

4. **Review logs:**
   Check Claude Code logs for specific errors

---

### Tools Not Available

**Problem:** Agent can't access specified tools

**Error Message:**
```
Error: Tool 'Write' not available
```

**Solution:**

1. **Verify tools in agent.json:**
   ```json
   {
     "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
   }
   ```

2. **Check permissions:**
   - Some tools may require specific permissions
   - Verify Claude Code has file system access

3. **Restart agent:**
   - Exit current task
   - Restart Claude Code
   - Try again

---

### Agent Produces Wrong Output

**Problem:** Agent doesn't follow instructions

**Symptoms:**
- Ignores prompt directives
- Wrong output format
- Missing expected sections

**Solution:**

1. **Review prompt.md:**
   - Check for contradictions
   - Ensure clear instructions
   - Add specific examples

2. **Make prompt more specific:**
   ```markdown
   ## Output Format

   Generate EXACTLY this structure:

   # Title

   ## Section 1
   [content]

   ## Section 2
   [content]
   ```

3. **Add constraints:**
   ```markdown
   ## Constraints
   - ALWAYS include file paths
   - NEVER skip error handling
   - MUST provide code examples
   ```

4. **Test with simple task:**
   - Verify basic functionality
   - Gradually increase complexity

## Integration Issues

### Agent Can't Read Files

**Problem:** Agent fails to read specified files

**Error Message:**
```
Error: Cannot read file 'src/component.jsx'
```

**Solution:**

1. **Verify file exists:**
   ```bash
   ls -la src/component.jsx
   ```

2. **Check file path:**
   - Use absolute paths: `C:\Users\...\file.js`
   - Or relative to working directory: `./src/file.js`

3. **Check permissions:**
   ```bash
   # Linux/Mac
   chmod 644 src/component.jsx

   # Windows - check file properties
   ```

4. **Verify Read tool is available:**
   ```json
   {
     "tools": ["Read", ...]
   }
   ```

---

### Agent Can't Write Files

**Problem:** Agent fails to create/modify files

**Error Message:**
```
Error: Permission denied writing to 'output.md'
```

**Solution:**

1. **Check directory permissions:**
   ```bash
   # Linux/Mac
   chmod 755 output-directory/

   # Windows - check folder permissions
   ```

2. **Verify Write tool is available:**
   ```json
   {
     "tools": ["Write", ...]
   }
   ```

3. **Check disk space:**
   ```bash
   # Linux/Mac
   df -h

   # Windows
   dir
   ```

4. **Ensure directory exists:**
   ```bash
   mkdir -p path/to/output
   ```

---

### Agent Can't Execute Commands

**Problem:** Bash tool fails

**Error Message:**
```
Error: Command execution failed
```

**Solution:**

1. **Verify Bash tool is available:**
   ```json
   {
     "tools": ["Bash"]
   }
   ```

2. **Check command syntax:**
   ```bash
   # Test command manually first
   npm test

   # Then use in agent
   ```

3. **Check PATH:**
   ```bash
   # Ensure required commands are in PATH
   which npm
   which node
   ```

4. **Use absolute paths:**
   ```bash
   # Instead of
   npm test

   # Use
   /usr/local/bin/npm test
   ```

## Performance Issues

### Agent Runs Slowly

**Problem:** Agent takes too long to complete

**Symptoms:**
- Timeouts
- Slow file processing
- Delayed responses

**Solution:**

1. **Reduce scope:**
   ```markdown
   ## Optimization
   - Process max 50 files
   - Skip files larger than 5000 lines
   - Limit dependency depth to 2 levels
   ```

2. **Use efficient tools:**
   ```markdown
   Instead of:
   - Read all files, then filter

   Use:
   - Grep to find relevant files
   - Read only matched files
   ```

3. **Add progress indicators:**
   ```markdown
   ## Process
   1. Found 100 files
   2. Processing batch 1/10...
   3. Processing batch 2/10...
   ```

4. **Batch operations:**
   ```markdown
   Instead of:
   - Read file1, analyze, write report
   - Read file2, analyze, write report

   Use:
   - Read all files
   - Analyze all files
   - Write combined report
   ```

---

### Agent Uses Too Much Memory

**Problem:** System runs out of memory

**Symptoms:**
- System slowdown
- Crash/freeze
- Out of memory errors

**Solution:**

1. **Limit file size:**
   ```markdown
   ## Constraints
   - Skip files larger than 5000 lines
   - Process files in batches of 10
   - Clear data between batches
   ```

2. **Stream large files:**
   ```markdown
   ## For Large Files
   - Read first 1000 lines for quick scan
   - Process incrementally
   - Report progress
   ```

3. **Add memory limits to prompt:**
   ```markdown
   ## Memory Management
   - Do not load entire file if > 1MB
   - Process in chunks
   - Report if file too large
   ```

---

### Agent Timeouts

**Problem:** Agent doesn't complete in time

**Error Message:**
```
Error: Operation timed out
```

**Solution:**

1. **Set realistic timeouts:**
   ```markdown
   ## Expected Duration
   - Small projects: 1-2 minutes
   - Medium projects: 5-10 minutes
   - Large projects: 15-20 minutes
   ```

2. **Add checkpoints:**
   ```markdown
   ## Process
   1. Phase 1 (1 min): File discovery
   2. Phase 2 (3 min): Analysis
   3. Phase 3 (1 min): Report generation
   ```

3. **Provide partial results:**
   ```markdown
   ## If Timeout
   - Return analysis completed so far
   - Note incomplete sections
   - Suggest resuming from checkpoint
   ```

## Documentation Issues

### README Not Displaying

**Problem:** README.md doesn't render properly

**Symptoms:**
- Broken formatting
- Missing sections
- Code blocks not rendering

**Solution:**

1. **Check markdown syntax:**
   ```bash
   # Use markdown linter
   npm install -g markdownlint-cli
   markdownlint README.md
   ```

2. **Verify code blocks:**
   ````markdown
   Correct:
   ```javascript
   const x = 1;
   ```

   Incorrect:
   ``javascript
   const x = 1;
   ``
   ````

3. **Check special characters:**
   ```markdown
   Escape special characters:
   \# Not a heading
   \* Not a bullet
   ```

---

### Examples Not Clear

**Problem:** Users don't understand how to use agent

**Solution:**

1. **Add complete examples:**
   ```markdown
   # Example: Complete Workflow

   ## Scenario
   You have a React component with 500 lines

   ## Step 1: Invoke Agent
   \`\`\`
   Analyze src/components/Dashboard.jsx
   \`\`\`

   ## Step 2: Review Output
   [Show actual output]

   ## Step 3: Take Action
   [Show what to do next]
   ```

2. **Include screenshots/output:**
   ```markdown
   ## Expected Output
   \`\`\`markdown
   # Analysis Report

   ## Issues Found
   1. Component too large (500 lines)
   ...
   \`\`\`
   ```

3. **Add troubleshooting section:**
   ```markdown
   ## Common Issues

   ### Issue: No issues detected
   **Cause:** File already follows best practices
   **Action:** No changes needed
   ```

## Getting More Help

### Debug Mode

Enable debug mode in agent:
```markdown
## Debug Mode

When invoked with "debug" flag:
- Show all file reads
- Log all tool calls
- Display intermediate results
- Report processing times
```

### Logging

Add logging to prompt:
```markdown
## Logging

Always log:
- Files processed: X/Y
- Issues found: N
- Processing time: T seconds
- Memory used: M MB
```

### Community Support

1. Check existing issues in repository
2. Search documentation
3. Review similar agents
4. Open new issue with:
   - Agent name and version
   - Error message
   - Steps to reproduce
   - Expected vs actual behavior

## Quick Reference

### Checklist for Issues

- [ ] Verified file structure
- [ ] Checked JSON syntax
- [ ] Validated tool names
- [ ] Reviewed prompt.md
- [ ] Tested with simple input
- [ ] Checked logs
- [ ] Restarted Claude Code
- [ ] Reviewed documentation

### Common Solutions

| Issue | Quick Fix |
|-------|-----------|
| Script won't run | Check execution policy/permissions |
| JSON error | Validate with JSON linter |
| Agent not found | Check location and restart |
| Tool not available | Add to agent.json |
| Slow performance | Reduce scope, batch operations |
| Wrong output | Make prompt more specific |
| Can't read files | Check paths and permissions |
| Timeout | Add checkpoints, return partial results |

## Summary

Most issues fall into these categories:
1. **Setup**: Permissions, paths, configuration
2. **Configuration**: JSON syntax, required fields
3. **Runtime**: Tool availability, file access
4. **Performance**: Scope, batching, memory
5. **Output**: Prompt clarity, examples

Follow the troubleshooting steps systematically, and refer to other documentation as needed.

For additional help:
- [Getting Started](getting-started.md)
- [Agent Development](agent-development.md)
- [Best Practices](best-practices.md)
