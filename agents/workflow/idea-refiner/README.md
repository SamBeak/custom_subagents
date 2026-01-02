# Idea Refiner

## Overview

A specialized refinement agent that synthesizes expansion possibilities and critical feedback into improved, actionable ideas. Integrates diverse inputs to produce coherent, strengthened concepts ready for validation.

## Category

Workflow / Synthesis

## Capabilities

- Integrates expansion directions with critique feedback
- Strengthens weak points while preserving core value
- Creates clear value propositions
- Develops phased execution plans
- Documents all refinement decisions

## Refinement Principles

| Principle | Korean | Purpose |
|-----------|--------|---------|
| **Selective Synthesis** | 선택적 통합 | Choose best directions, discard weak ones |
| **Weakness Fortification** | 약점 강화 | Transform risks into mitigations |
| **Value Crystallization** | 가치 결정화 | Clarify core value proposition |
| **Actionability Enhancement** | 실행력 강화 | Make concept executable |

## Usage

### As Part of Orchestration

This agent is typically invoked by `idea-developer` orchestrator:

```
Task({
  subagent_type: "idea-refiner",
  prompt: "[Original + expansions + critiques]",
  description: "Refine and synthesize for iteration N"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-refiner",
  prompt: "원본 아이디어: [X]
           확장 방향: [Y]
           비판 포인트: [Z]
           이를 통합하여 정제된 버전을 만들어주세요",
  description: "Synthesize and refine idea"
})
```

## Input/Output Format

### Input

```markdown
## Refinement Request

### Original Idea
### Expander Output
### Critic Output
### Context
- Iteration: [N of 3]
- Focus Areas: [if specified]
```

### Output

```markdown
## Refinement Report

### Refined Concept
### Value Proposition
### Risk Mitigations Integrated
### Execution Plan (Phased)
### Refinement Changelog
### Validation Brief
```

## Best Practices

1. **Address All Critical Issues**: Don't ignore major critiques
2. **Preserve Core Value**: Strengthen, don't replace
3. **Be Specific**: Actionable tasks, not vague plans
4. **Document Decisions**: Explain what was kept/changed/excluded

## Limitations

- Quality depends on quality of prior agent outputs
- Cannot resolve fundamental idea viability issues
- Execution plans are estimates, not guarantees

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
