# Idea Critic

## Overview

A specialized critical analysis agent that identifies weaknesses, risks, and limitations in ideas. Acts as a constructive Devil's Advocate to strengthen concepts through rigorous examination.

## Category

Workflow / Analysis

## Capabilities

- Analyzes ideas across 5 critique dimensions
- Rates severity of issues (Critical/Major/Minor)
- Assesses expansion direction viability
- Provides constructive improvement suggestions
- Identifies both risks AND strengths

## 5 Critique Dimensions

| Dimension | Korean | Focus |
|-----------|--------|-------|
| **Logic & Coherence** | 논리적 일관성 | Premises, contradictions, assumptions |
| **Feasibility** | 실현 가능성 | Technical, resource, timeline viability |
| **Market & Competition** | 시장 및 경쟁 | Competitors, differentiation, timing |
| **Risk Scenarios** | 리스크 시나리오 | Failure modes, external threats |
| **User & Value** | 사용자 및 가치 | Problem validity, willingness to pay |

## Usage

### As Part of Orchestration

This agent is typically invoked by `idea-developer` orchestrator:

```
Task({
  subagent_type: "idea-critic",
  prompt: "[Idea + expansions from expander]",
  description: "Analyze weaknesses for iteration N"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-critic",
  prompt: "구독형 식료품 배달 서비스 - 
           주요 리스크와 약점을 분석해주세요",
  description: "Critical analysis of business idea"
})
```

## Input/Output Format

### Input

```markdown
## Critique Request

### Original Idea
[Description]

### Expansion Output
[Summary from Expander]

### Context
- Iteration: [N of 3]
- Focus Areas: [if specified]
```

### Output

```markdown
## Critical Analysis Report

### Critical Findings (by dimension)
### Expansion Direction Assessment
### Priority Issues for Refinement
### Strengths Identified
### Handoff to Refiner Agent
```

## Best Practices

1. **Be Constructive**: Every criticism should enable improvement
2. **Be Balanced**: Acknowledge strengths alongside weaknesses
3. **Be Specific**: Concrete issues, not vague concerns
4. **Be Fair**: Give idea benefit of reasonable doubt

## Limitations

- Critique quality depends on input detail
- Cannot validate market claims with real data
- Best suited for business/product/technical ideas

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
