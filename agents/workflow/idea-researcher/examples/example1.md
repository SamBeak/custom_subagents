# Example: AI Code Review Tool Market Research

## Input

```
아이디어: AI 기반 코드 리뷰 자동화 도구
조사 범위: 시장 현황, 경쟁 제품, 기술 옵션
```

## Output

```markdown
## Research Report

### Research Summary
- **Idea**: AI 기반 코드 리뷰 자동화 도구
- **Research Scope**: 시장, 경쟁, 기술
- **Sources Consulted**: 12
- **Research Date**: 2026-01-02

### Market Insights

#### Market Size & Growth
| Metric | Value | Source | Reliability |
|--------|-------|--------|-------------|
| Global Code Review Market | $1.2B (2024) | Gartner Report | High |
| CAGR | 12.5% | Statista | High |
| AI DevTools Segment | $450M | Industry Analysis | Medium |

#### Key Trends
1. **AI-First Development**: 개발자의 67%가 AI 보조 도구 사용 - Source: Stack Overflow 2024
2. **Security Focus**: 보안 취약점 자동 탐지 수요 급증 - Source: GitHub Blog
3. **CI/CD 통합**: 파이프라인 통합이 핵심 요구사항 - Source: DevOps Reports

### Competitive Landscape

#### Identified Competitors
| Competitor | Type | Key Features | Pricing | Positioning |
|------------|------|--------------|---------|-------------|
| GitHub Copilot | 직접 | AI 코드 제안, 리뷰 | $19/월 | 대중 시장 |
| CodeRabbit | 직접 | PR 자동 리뷰 | $12/월 | SMB 타겟 |
| Codacy | 직접 | 정적 분석 + AI | $15/월 | 엔터프라이즈 |
| SonarQube | 간접 | 정적 분석 | Free-$150/월 | 코드 품질 |

### Technology Landscape

#### Available Solutions
| Solution | Type | Maturity | Cost | Notes |
|----------|------|----------|------|-------|
| OpenAI API | API | 성숙 | $0.03/1K tokens | GPT-4 기반 |
| Claude API | API | 성숙 | $0.015/1K tokens | 긴 컨텍스트 |
| CodeLlama | 오픈소스 | 중간 | Self-host 비용 | 코드 특화 |
| Tree-sitter | 오픈소스 | 성숙 | Free | AST 파싱 |

### Key Findings

#### Opportunities
1. 한국어 코드 리뷰 코멘트 지원 시장 공백
2. 보안 취약점 + AI 리뷰 통합 솔루션 부재
3. 소규모 팀 대상 저가 솔루션 수요

#### Threats/Challenges
1. GitHub Copilot의 시장 지배력 강화
2. LLM API 비용 상승 리스크
3. 코드 보안/프라이버시 우려

### Sources

| # | URL | Type | Reliability | Accessed |
|---|-----|------|-------------|----------|
| 1 | gartner.com/devtools-report | Report | High | 2026-01-02 |
| 2 | stackoverflow.com/survey/2024 | Survey | High | 2026-01-02 |
| 3 | github.com/features/copilot | Product | High | 2026-01-02 |
| 4 | coderabbit.ai | Product | High | 2026-01-02 |

### Handoff to Next Agent
- **Key Data Points**: 시장 규모 $1.2B, 연 12.5% 성장, 주요 경쟁사 4개
- **Recommended Focus Areas**: 한국어 지원, 보안 통합, SMB 세그먼트
```
