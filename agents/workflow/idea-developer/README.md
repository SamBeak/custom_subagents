# Idea Developer

## Overview

A Multi-Agent Orchestrator (v3.0) that systematically develops and refines ideas through **10 specialized agents** with parallel and sequential execution. Transforms initial concepts into well-developed, actionable plans with complete monetization strategies and investor pitch materials.

## Category

Workflow / Orchestration

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        IDEA-DEVELOPER (Orchestrator)                 │
├──────────────────────────────────────────────────────────────────────┤
│  ┌─────────────── PARALLEL RESEARCH PHASE ──────────────┐            │
│  │  researcher ─┬─ competitor-analyzer ─┬─ user-persona │ ← 동시실행 │
│  └──────────────┴───────────────────────┴───────────────┘            │
│                              ↓                                        │
│  ┌─────────────── DEVELOPMENT CYCLE ────────────────────┐            │
│  │  expander → critic → refiner → feasibility → validator           │
│  └───────────────────────────┬──────────────────────────┘            │
│                              ↓                                        │
│              Score < 7: Iterate | Score ≥ 7: Continue                │
│                              ↓                                        │
│  ┌─────────────── STRATEGY & OUTPUT ────────────────────┐            │
│  │  monetization-strategist → pitch-generator            │            │
│  └───────────────────────────┬──────────────────────────┘            │
│                              ↓                                        │
│                     FINAL OUTPUT PACKAGE                              │
└──────────────────────────────────────────────────────────────────────┘
```

## Key Features (v3.0)

- **10 Specialized Agents**: Complete idea-to-pitch pipeline
- **Parallel Research**: 3 agents run simultaneously for efficiency
- **Monetization Strategy**: Business model, pricing, revenue projections
- **Pitch Materials**: One-liner, elevator pitch, deck structure
- **Iterative Refinement**: Up to 3 cycles based on validation score

## Delegated Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `idea-researcher` | Research (Parallel) | RAG/Fetch 기반 외부 정보 수집 |
| `idea-competitor-analyzer` | Research (Parallel) | 경쟁 환경 심층 분석 |
| `idea-user-persona` | Research (Parallel) | 타겟 사용자 페르소나 생성 |
| `idea-expander` | Development | 가능성 확장 (5개 렌즈) |
| `idea-critic` | Development | 약점 및 리스크 분석 |
| `idea-refiner` | Development | 통합 및 정제 |
| `idea-feasibility-checker` | Development | 기술적 실현 가능성 평가 |
| `idea-validator` | Development | 완성도 평가 (7점 기준) |
| `idea-monetization-strategist` | Strategy | 수익화 전략, BM Canvas |
| `idea-pitch-generator` | Output | 피치덱, 엘리베이터 피치 |

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

A comprehensive package including:

1. **Refined Concept**: Clarified, strengthened idea
2. **Value Proposition**: Clear differentiation statement
3. **Execution Plan**: Phased tasks with milestones
4. **Risk Analysis**: Identified risks with mitigations
5. **Business Model**: Canvas, pricing, revenue projections
6. **Pitch Materials**: One-liner, elevator pitches, deck structure
7. **Development History**: All iteration details

## Workflow

1. **Initialize**: Parse idea, create working document
2. **Parallel Research**: Market, competition, user personas (simultaneous)
3. **Iterate** (max 3 cycles):
   - Expand possibilities
   - Critique weaknesses
   - Refine and synthesize
   - Check feasibility
   - Validate completeness
4. **Strategy**: Monetization and business model design
5. **Output**: Generate pitch materials
6. **Finalize**: Assemble comprehensive package

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

- **v3.0.0** (2026-01-02): Major update - 10 agents, parallel research, monetization, pitch generation
- **v2.0.0** (2026-01-02): Added 4 specialized agents (researcher, competitor, user-persona, feasibility)
- **v1.0.0** (2026-01-02): Initial release with 4-agent orchestration

## Author

Custom Subagents Repository
