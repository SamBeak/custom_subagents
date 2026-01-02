# Idea Pitch Generator

## Overview

A communication and presentation agent that transforms developed ideas into compelling pitch materials. Creates investor decks, elevator pitches, one-liners, and audience-specific messaging.

## Category

Workflow / Communication

## Key Features

- **One-Liner Generation**: Memorable 10-word descriptions
- **Elevator Pitches**: 30/60/90-second scripts
- **Pitch Deck Structure**: 12-15 slide investor deck
- **Audience Customization**: Investor/Customer/Partner variants
- **Storytelling Framework**: Problem-Solution-Impact structure
- **One-Pager Design**: Ready-to-design content blocks

## Pitch Formats

| Format | Duration/Length | Use Case |
|--------|-----------------|----------|
| One-liner | 10 words | Social, email subject |
| 30-sec pitch | 75 words | Networking |
| 60-sec pitch | 150 words | Intro meetings |
| 90-sec pitch | 225 words | Demo intro |
| Full deck | 12-15 slides | Investor meeting |

## Usage

### As Part of Orchestration

```
Task({
  subagent_type: "idea-pitch-generator",
  prompt: "[Developed idea + monetization] - 투자자 피치 자료를 생성해줘",
  description: "Generate investor pitch materials"
})
```

### Standalone Usage

```
Task({
  subagent_type: "idea-pitch-generator",
  prompt: "30초 엘리베이터 피치를 작성해줘",
  description: "Create elevator pitch"
})
```

## Output Format

```markdown
## Pitch Materials Package

### One-Liner
> "[Memorable tagline]"

### Elevator Pitches
#### 30-Second Version
[Script]

#### 60-Second Version
[Extended script]

### Pitch Deck Outline
| Slide | Title | Key Message |
|-------|-------|-------------|
| 1 | Title | Company + tagline |
| 2 | Problem | Pain point |
| ... | ... | ... |

### Audience Variants
#### For Investors
[Key emphasis]

#### For Customers
[Key emphasis]
```

## Integration

| Direction | Agent | Data Passed |
|-----------|-------|-------------|
| Input ← | idea-refiner | Refined concept |
| Input ← | idea-monetization-strategist | Business model, financials |
| Input ← | idea-competitor-analyzer | Differentiation |
| Input ← | idea-user-persona | Target audience |
| Input ← | idea-validator | Validation scores |
| Output → | idea-developer | Complete pitch package |

## Storytelling Frameworks

### Problem-Solution-Impact
```
"Every day, [users] struggle with [problem].
We built [solution] that [benefit].
As a result, [impact]."
```

### Before-After-Bridge
```
Before: [Painful state]
After: [Desired state]
Bridge: [Your solution]
```

## Limitations

- Pitch decks are structure/content only (no visual design)
- Effectiveness depends on quality of input data
- Should be refined with real audience feedback

## Version History

- **v1.0.0** (2026-01-02): Initial release

## Author

Custom Subagents Repository
