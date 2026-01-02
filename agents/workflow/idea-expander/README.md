# Idea Expander

## Overview

A specialized expansion agent that broadens the possibilities of any given idea using structured creative thinking methodologies. Explores diverse directions, uncovers hidden potential, and generates creative variations.

## Category

Workflow / Ideation

## Capabilities

- Applies 5 expansion lenses systematically
- Generates 5-7 distinct development directions
- Identifies cross-cutting themes and patterns
- Rates potential of each direction
- Prepares structured handoff for critique phase

## 5 Expansion Lenses

| Lens | Korean | Purpose |
|------|--------|---------|
| **What-If** | 가정 변경 | Challenge constraints, explore alternatives |
| **Combination** | 조합 탐색 | Merge with existing solutions/technologies |
| **Scale** | 규모 변경 | Vary dimensions (10x larger, niche focus) |
| **Inversion** | 역발상 | Flip perspectives, opposite approaches |
| **Analogy** | 유추 적용 | Learn from other domains/industries |

## Usage

### As Part of Orchestration

This agent is typically invoked by `idea-developer` orchestrator:

```
Task({
  subagent_type: "idea-expander",
  prompt: "[Idea + context from orchestrator]",
  description: "Expand possibilities for iteration N"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-expander",
  prompt: "음성 인식 기반 메모 앱 - 
           확장 가능한 방향을 탐색해주세요",
  description: "Explore expansion directions"
})
```

## Input/Output Format

### Input

```markdown
## Expansion Request

### Idea to Expand
[Description]

### Context
- Domain: [domain]
- Iteration: [N of 3]
- Previous Insights: [if applicable]
```

### Output

```markdown
## Idea Expansion Report

### Expansion Results
#### Direction 1-7: [Name, Description, Potential Rating]

### Cross-Cutting Themes
### Top 3 Recommendations
### Areas for Critical Review
### Handoff to Critic Agent
```

## Best Practices

1. **Apply All Lenses**: Don't skip difficult lenses
2. **Go Beyond Obvious**: Include at least 2 non-obvious directions
3. **Be Specific**: Concrete directions, not vague possibilities
4. **Balance Feasibility**: Range from practical to ambitious

## Limitations

- Requires clear initial concept to expand from
- Maximum 10 directions to maintain quality
- Works best with business/product/technical ideas

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
