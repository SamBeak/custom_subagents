# Idea Competitor Analyzer

## Overview

A competitive intelligence agent that performs deep analysis of the competitive landscape. Identifies direct and indirect competitors, compares features and pricing, maps market positioning, and discovers differentiation opportunities.

## Category

Workflow / Analysis

## Key Features

- **Competitor Identification**: Direct, indirect, and alternative solutions
- **Feature Comparison**: Matrix-based analysis
- **Pricing Analysis**: Models, tiers, hidden costs
- **Positioning Map**: Visual quadrant analysis
- **Differentiation Strategy**: Actionable opportunities

## Competitor Types

| Type | Definition | Example |
|------|------------|---------|
| Direct | Same problem, same approach | Competitor A vs Competitor B |
| Indirect | Same problem, different approach | Notion vs Physical notebook |
| Alternative | Current workaround | Spreadsheets, manual processes |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-competitor-analyzer",
  prompt: "[Idea + competitor list] - 경쟁 환경을 심층 분석해줘",
  description: "Analyze competitive landscape"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-competitor-analyzer",
  prompt: "프로젝트 관리 도구 시장의 주요 경쟁사와 차별화 기회를 분석해줘",
  description: "Competitive analysis for PM tools"
})
```

## Output Format

```markdown
## Competitive Analysis Report

### Competitive Landscape Overview
- Market map visualization
- Competition intensity rating

### Detailed Competitor Profiles
- Per-competitor: features, pricing, strengths, weaknesses

### Feature Comparison Matrix
- Side-by-side capability analysis

### Positioning Analysis
- Quadrant map with white spaces

### Differentiation Opportunities
- Top 3 actionable strategies

### Strategic Recommendations
- Entry strategy
- Competitive response forecast
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Input ← | idea-researcher | Initial competitor list |
| Input ← | idea-developer | Idea description |
| Output → | idea-expander | White space opportunities |
| Output → | idea-critic | Competitive risks |
| Output → | idea-refiner | Differentiation strategy |

## Limitations

- Based on publicly available information only
- Cannot access internal competitor data
- Market dynamics may change rapidly

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
