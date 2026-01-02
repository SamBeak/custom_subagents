# Idea Monetization Strategist

## Overview

A business model and monetization strategy agent that transforms refined ideas into viable commercial plans. Designs revenue models, pricing strategies, unit economics, and go-to-market plans.

## Category

Workflow / Strategy

## Key Features

- **Business Model Canvas**: Complete 9-block canvas generation
- **Revenue Model Design**: SaaS, marketplace, freemium, etc.
- **Pricing Strategy**: Value-based, competitive, tiered pricing
- **Unit Economics**: CAC, LTV, payback period analysis
- **Revenue Projection**: 3-year forecast with scenarios
- **Go-to-Market Strategy**: Channel and launch planning

## Revenue Models Supported

| Model | Best For | Key Metric |
|-------|----------|------------|
| Subscription | Recurring value | MRR/ARR |
| Usage-based | Variable consumption | Revenue per unit |
| Freemium | Network effects | Conversion rate |
| Transaction | Marketplace | GMV, take rate |
| Licensing | Enterprise | Deal size |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-monetization-strategist",
  prompt: "[Refined idea] - 수익화 전략을 설계해줘",
  description: "Design monetization strategy"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-monetization-strategist",
  prompt: "B2B SaaS 제품의 가격 티어와 수익 모델을 설계해줘",
  description: "Pricing and revenue model design"
})
```

## Output Format

```markdown
## Monetization Strategy Report

### Business Model Canvas
[Complete 9-block canvas]

### Revenue Model
- Primary model with rationale
- Secondary revenue streams

### Pricing Strategy
- Tier structure (Free/Pro/Enterprise)
- Pricing rationale

### Unit Economics
| Metric | Target |
|--------|--------|
| CAC | $X |
| LTV | $Y |
| LTV:CAC | 3:1+ |

### Revenue Projection (3-Year)
| Year | Pessimistic | Base | Optimistic |
|------|-------------|------|------------|
| Y1 | $X | $Y | $Z |

### Go-to-Market Strategy
- Target segments
- Channel strategy
- Launch timeline
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Input ← | idea-refiner | Refined value proposition |
| Input ← | idea-competitor-analyzer | Competitor pricing |
| Input ← | idea-user-persona | Customer segments, WTP |
| Input ← | idea-feasibility-checker | Cost structure |
| Output → | idea-pitch-generator | Financial highlights |
| Output → | idea-validator | Monetization viability |

## Limitations

- Projections are estimates based on assumptions
- Market dynamics may change rapidly
- Requires validation with real customers

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
