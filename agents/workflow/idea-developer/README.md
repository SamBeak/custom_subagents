# Idea Developer

## Overview

A Multi-Agent Orchestrator that systematically develops and refines ideas through coordinated expansion, critique, refinement, and validation cycles. Transforms initial concepts into well-developed, actionable plans.

## Category

Workflow / Orchestration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IDEA-DEVELOPER                           │
│                    (Orchestrator)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │idea-expander │→ │ idea-critic  │→ │ idea-refiner │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
│                            ↓                                │
│                   ┌──────────────┐                         │
│                   │idea-validator│                         │
│                   └──────────────┘                         │
│                            ↓                                │
│              Score < 7: Iterate | Score ≥ 7: Finalize      │
└─────────────────────────────────────────────────────────────┘
```

## Capabilities

- Orchestrates 4 specialized agents for comprehensive idea development
- Manages iterative refinement cycles (up to 3 iterations)
- Tracks development history and decision rationale
- Produces structured final reports with execution plans
- Handles context preservation across agent handoffs

## Delegated Agents

| Agent | Role | Purpose |
|-------|------|---------|
| `idea-expander` | Expansion | Explore possibilities, generate variations |
| `idea-critic` | Critique | Identify risks, weaknesses, blind spots |
| `idea-refiner` | Refinement | Synthesize feedback, strengthen concept |
| `idea-validator` | Validation | Evaluate completeness, decide iteration |

## Usage

### Basic Example

```
Task({
  subagent_type: "idea-developer",
  prompt: "AI 기반 코드 리뷰 자동화 도구",
  description: "Develop this SaaS idea into an actionable plan"
})
```

### With Context

```
Task({
  subagent_type: "idea-developer",
  prompt: "팀 내 지식 공유 시스템 구축. 
           제약사항: 예산 $50K, 6개월 내 구현, 
           기존 Slack/Notion 통합 필요",
  description: "Develop business process improvement idea"
})
```

## Input/Output Format

### Input

- **Required**: Initial idea description (any length)
- **Optional**: Constraints, target users, specific focus areas

### Output

A comprehensive development report including:

1. **Refined Concept**: Clarified, strengthened idea
2. **Value Proposition**: Clear differentiation statement
3. **Execution Plan**: Phased tasks with milestones
4. **Risk Analysis**: Identified risks with mitigations
5. **Development History**: All iteration details

## Workflow

1. **Initialize**: Parse idea, create working document
2. **Iterate** (max 3 cycles):
   - Expand possibilities
   - Critique weaknesses
   - Refine and synthesize
   - Validate completeness
3. **Finalize**: Generate comprehensive report

## Scoring System

| Score | Interpretation | Action |
|-------|----------------|--------|
| 9-10 | Excellent | Ready for execution |
| 7-8 | Good | Proceed with minor notes |
| 5-6 | Fair | Another iteration needed |
| 3-4 | Weak | Significant work required |
| 1-2 | Poor | Fundamental rethinking |

## Best Practices

1. **Provide Context**: More context = better development
2. **Specify Constraints**: Budget, timeline, resources
3. **Define Success**: What does a good outcome look like?
4. **Be Patient**: Quality development takes time

## Limitations

- Maximum 3 development iterations per session
- Best suited for business/product/process ideas
- Requires clear initial concept (not brainstorming from zero)
- Output quality depends on input specificity

## Version History

- **v1.0.0** (2026-01-02): Initial release with 4-agent orchestration

## Author

Custom Subagents Repository
