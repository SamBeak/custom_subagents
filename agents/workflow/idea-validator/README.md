# Idea Validator

## Overview

A specialized validation agent that evaluates the completeness and quality of refined ideas. Serves as the quality gate that determines whether an idea is ready for execution or needs further iteration.

## Category

Workflow / Evaluation

## Capabilities

- Evaluates ideas across 5 quality dimensions
- Provides calibrated scores (1-10 scale)
- Determines iteration necessity (threshold: 7)
- Offers specific improvement suggestions
- Enables informed Go/No-Go decisions

## 5 Evaluation Dimensions

| Dimension | Korean | Max Points | Focus |
|-----------|--------|------------|-------|
| **Clarity** | 명확성 | 2 | Core concept, value prop, scope |
| **Feasibility** | 실현 가능성 | 2 | Technical, resource, timeline |
| **Differentiation** | 차별성 | 2 | Unique value, competitive advantage |
| **Completeness** | 완결성 | 2 | Execution plan, milestones, tasks |
| **Risk Coverage** | 리스크 대응 | 2 | Risk identification, mitigations |

## Scoring Guide

| Score | Interpretation | Decision |
|-------|----------------|----------|
| 9-10 | Excellent | Ready for immediate execution |
| 7-8 | Good | Proceed with minor refinements |
| 5-6 | Fair | Another iteration needed |
| 3-4 | Weak | Significant issues to address |
| 1-2 | Poor | Fundamental rethinking needed |

## Usage

### As Part of Orchestration

This agent is typically invoked by `idea-developer` orchestrator:

```
Task({
  subagent_type: "idea-validator",
  prompt: "[Refined idea from refiner]",
  description: "Evaluate completeness for iteration N"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-validator",
  prompt: "정제된 아이디어: [상세 내용]
           이 아이디어의 완성도를 평가해주세요",
  description: "Validate idea readiness"
})
```

## Input/Output Format

### Input

```markdown
## Validation Request

### Refined Concept
[Complete refinement report]

### Context
- Iteration: [N of 3]
- Previous Validation: [if applicable]
```

### Output

```markdown
## Validation Report

### Dimension Scores (detailed tables)
### Score Summary
### Overall Assessment
### Iteration Guidance (if score < 7)
### Decision Recommendation
```

## Decision Rules

- **Score ≥ 7**: Proceed to finalization
- **Score < 7 AND iteration < 3**: Recommend next iteration
- **Score < 7 AND iteration = 3**: Proceed with caveats noted

## Best Practices

1. **Be Objective**: Score based on evidence, not impression
2. **Be Consistent**: Apply same criteria across iterations
3. **Be Actionable**: Low scores need clear improvement path
4. **Be Honest**: Don't inflate scores to avoid iteration

## Limitations

- Cannot validate with real market data
- Scores are relative assessments, not absolute measures
- Final human judgment still required for Go/No-Go

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
