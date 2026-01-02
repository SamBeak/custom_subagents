# Idea Feasibility Checker

## Overview

A technical feasibility analysis agent that evaluates implementation viability. Identifies required technology stacks, assesses development complexity, estimates costs, and predicts technical debt.

## Category

Workflow / Analysis

## Key Features

- **Tech Stack Identification**: Required technologies per feature
- **Build vs Buy Analysis**: Custom development vs SaaS/API options
- **Complexity Rating**: 1-5 scale with clear criteria
- **Cost Estimation**: Initial and ongoing costs
- **Risk Assessment**: Technical dependencies and scaling concerns

## Complexity Rating Guide

| Level | Description | Example |
|-------|-------------|---------|
| 1 | Simple | Static website, basic CRUD |
| 2 | Moderate | Auth-enabled web app |
| 3 | Complex | Real-time features, multi-integration |
| 4 | Very Complex | ML/AI integration, large-scale data |
| 5 | Extremely Complex | Distributed systems, real-time ML |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-feasibility-checker",
  prompt: "[Refined idea from refiner] - 기술적 실현 가능성을 평가해줘",
  description: "Evaluate technical feasibility"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-feasibility-checker",
  prompt: "실시간 음성 번역 앱의 기술 스택과 개발 난이도를 분석해줘",
  description: "Technical feasibility assessment"
})
```

## Output Format

```markdown
## Technical Feasibility Report

### Assessment Summary
- Overall Feasibility: High/Medium/Low
- Complexity Rating: 1-5
- Estimated MVP Timeline

### Recommended Tech Stack
- Frontend, Backend, Database, Infrastructure

### Build vs Buy Analysis
- Component-by-component recommendation

### Development Estimation
- Team requirements, timeline, costs

### Risk Assessment
- Technical risks with mitigations
- Dependency risks
- Scaling considerations

### Go/No-Go Factors
- Viability checklist
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Input ← | idea-refiner | Refined concept |
| Input ← | idea-researcher | Technology options |
| Output → | idea-validator | Feasibility score basis |
| Output → | idea-refiner | Technical constraints |

## Limitations

- Estimates are approximations, not guarantees
- Cannot validate proprietary technology claims
- Best suited for software/digital products

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
