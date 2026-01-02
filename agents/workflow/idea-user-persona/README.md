# Idea User Persona

## Overview

A user research agent that generates detailed target user personas. Creates empathetic user profiles, maps customer journeys, identifies pain points, and analyzes adoption barriers using Jobs-to-be-Done framework.

## Category

Workflow / Analysis

## Key Features

- **Persona Generation**: Detailed, empathetic user profiles
- **Segmentation**: Priority-based user segment analysis
- **Journey Mapping**: As-Is and To-Be customer journeys
- **Pain Point Analysis**: Severity and frequency ratings
- **Adoption Barrier Identification**: With mitigation strategies

## Jobs-to-be-Done Framework

| Job Type | Description | Example |
|----------|-------------|---------|
| Functional | Task to accomplish | "Send meeting notes to team" |
| Emotional | Feeling to achieve | "Feel organized and in control" |
| Social | Perception by others | "Be seen as efficient leader" |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-user-persona",
  prompt: "[Idea + target user description] - 상세 페르소나를 생성해줘",
  description: "Generate detailed user personas"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-user-persona",
  prompt: "B2B SaaS 제품의 의사결정자 페르소나와 구매 여정을 분석해줘",
  description: "Generate B2B buyer personas"
})
```

## Output Format

```markdown
## User Persona Report

### User Segmentation
- Segments with priority ranking

### Primary Persona
- Demographics, background, goals
- Pain points with severity
- Jobs-to-be-Done
- Decision criteria

### User Journey Map
- Current state (As-Is)
- Opportunity areas
- Ideal state (To-Be)

### Adoption Barriers
- Barrier types with mitigation strategies

### Value Proposition Fit
- Problem-solution alignment score
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Input ← | idea-developer | Idea, target user |
| Input ← | idea-researcher | User data |
| Output → | idea-expander | User-centric directions |
| Output → | idea-critic | User-product fit issues |
| Output → | idea-refiner | Value proposition refinement |

## Limitations

- Personas are hypothetical without real user validation
- Best suited for B2B and B2C digital products
- Cultural/regional differences may require adjustment

## Version History

- **v1.0.0** (2026-01-02): Initial release with JTBD framework

## Author

Custom Subagents Repository
