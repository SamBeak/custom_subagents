# Idea Researcher

## Overview

A RAG-based research agent that leverages Fetch MCP and Web Search to collect real-time external information. Provides data-driven insights for idea development including market trends, competitor data, and technology references.

## Category

Workflow / Research

## Key Features

- **Real-time Information Retrieval**: Fetch MCP for live web data
- **Market Research**: Size, trends, growth rates
- **Technology Scouting**: APIs, open-source, SaaS options
- **Source Credibility Assessment**: High/Medium/Low reliability rating
- **Structured Output**: Ready for downstream agents

## Capabilities

| Capability | Description |
|------------|-------------|
| Web Search | Query-based information gathering |
| Document Fetch | Direct URL content extraction |
| Source Validation | Credibility and recency checks |
| Data Synthesis | Cross-reference multiple sources |
| Gap Identification | Flag areas needing more research |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-researcher",
  prompt: "AI 코드 리뷰 도구의 시장 현황, 경쟁 제품, 관련 기술을 조사해줘",
  description: "Gather market data and references"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-researcher",
  prompt: "밀키트 시장의 2024년 트렌드와 주요 플레이어를 조사해줘",
  description: "Market research for meal kit industry"
})
```

## Output Format

```markdown
## Research Report

### Market Insights
- Size, growth, trends with sources

### Competitive Landscape  
- Identified competitors with key details

### Technology Landscape
- Available solutions, APIs, tools

### Key Findings
- Opportunities and threats

### Sources
- All URLs with reliability ratings
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Output → | idea-expander | Market opportunities |
| Output → | idea-critic | Risk evidence |
| Output → | idea-competitor-analyzer | Initial competitor list |
| Output → | idea-feasibility-checker | Technology options |

## Limitations

- Cannot access paywalled content
- Real-time data may have delays
- Source reliability is estimated, not verified

## Version History

- **v1.0.0** (2026-01-02): Initial release with Fetch MCP integration

## Author

Custom Subagents Repository
