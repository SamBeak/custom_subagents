# weekly-report-ppt-prompt-generator

> Obsidian 주간업무보고 Markdown을 **생성형 AI용 PPT 프롬프트 Markdown**으로 변환하는 워크플로우 에이전트

## 개요

주간업무보고 노트(`주간업무보고/YYYY-MM-DD~YYYY-MM-DD.md`)를 분석하여, Gamma·Manus·ChatGPT·Claude·Gemini 등 **생성형 AI가 곧바로 PPT를 만들 수 있는 완결형 프롬프트 Markdown 파일**을 `주간업무보고_프롬프트/` 폴더에 저장합니다.

형제 에이전트 `weekly-report-ppt-generator`가 python-pptx로 `.pptx`를 직접 생성하는 것과 달리, 이 에이전트는 **프롬프트만** 생성합니다. 사용자는 산출된 프롬프트를 원하는 생성형 AI 서비스에 붙여넣어 PPT를 받습니다.

## 5파트 프롬프트 구조

| Part | 내용 |
|------|------|
| 1. 역할 지시 | 디자이너·보고서 전문가 역할, 청중(경영진), 목표(30초 핵심 파악) |
| 2. 슬라이드 구성 스펙 | 슬라이드별 번호·제목·요소·레이아웃 힌트 표 |
| 3. 디자인 가이드 | 폰트(맑은 고딕+나눔스퀘어 네오 Heavy), 강조색(#4472C4), 16:9 |
| 4. 원본 콘텐츠 블록 | 슬라이드별 파싱된 Markdown (프로젝트·WBS·다음주) |
| 5. 출력 포맷 지정 | Gamma/ChatGPT/Claude/Gemini/Manus별 최적화 |

## 워크플로우 (Phase 1~5)

| Phase | 이름 | 핵심 동작 |
|-------|------|----------|
| 1 | 입력 확정 | 주차 계산, Obsidian `주간업무보고/` 노트 읽기 |
| 2 | 노트 파싱 | frontmatter + 요약 + 프로젝트 + WBS + 다음주 추출 |
| 3 | 슬라이드 플랜 + **사용자 승인** | 표지 1 / 요약 1 / 프로젝트 X / WBS Y / 다음주 1 |
| 4 | 5파트 프롬프트 Markdown 작성 | 역할·스펙·디자인·콘텐츠·포맷 |
| 5 | 초안 확인 + 저장 | `주간업무보고_프롬프트/` 폴더에 저장 |

## 호출 예시

```
✅ "이번 주 주간업무보고 PPT 프롬프트 만들어줘"
✅ "주간보고서를 PPT 프롬프트로 변환"
✅ "2026-04-14~2026-04-20 주간업무보고를 PPT로 만들 수 있는 프롬프트 생성"
✅ "Gamma용 주간보고 프롬프트"
❌ "주간업무보고 PPT 만들어줘"           → weekly-report-ppt-generator 호출 (.pptx 직접 생성)
❌ "주간업무보고 작성해줘"                → weekly-work-reporter 호출 (Markdown 생성)
```

## 입출력

- **입력**: `주간업무보고/YYYY-MM-DD~YYYY-MM-DD.md`
- **출력**: `주간업무보고_프롬프트/YYYY-MM-DD~YYYY-MM-DD_ppt_prompt.md`
- **형식**: Markdown + YAML frontmatter (`type: ppt-prompt`, `source`, `slides`, `created`, `target-ai`)

## 대상 생성형 AI별 사용법

| 서비스 | 사용 방법 |
|--------|----------|
| Gamma.app | https://gamma.app/create → 프롬프트 전체 붙여넣기 |
| ChatGPT (Canvas) | 새 대화에서 붙여넣기 후 "PPT 파일로 만들어줘" |
| Claude (Artifacts) | 새 대화에서 붙여넣기 후 "Reveal.js 또는 PPTX로 출력" |
| Gemini | 새 대화에서 붙여넣기 후 Google Slides로 export |
| Manus | 에이전트 대화창에 붙여넣기 |

## 의존성

- Obsidian MCP (`mcp__obsidian__*`)
- Python (주차 계산)
- 선행 에이전트: `weekly-work-reporter` (주간 Markdown 노트 생성)

## 형제 에이전트와의 관계

| 에이전트 | 산출물 | 방식 |
|---------|-------|------|
| `weekly-work-reporter` | `주간업무보고/*.md` | 일일보고 → 주간 Markdown |
| `weekly-report-ppt-prompt-generator` (**본 에이전트**) | `주간업무보고_프롬프트/*_ppt_prompt.md` | 주간 Markdown → 생성형 AI용 프롬프트 |
| `weekly-report-ppt-generator` | `주간업무보고/*.pptx` | 주간 Markdown → python-pptx로 .pptx 직접 생성 |

## 변경 이력

| 날짜 | 변경 | 사유 |
|------|------|------|
| 2026-04-20 | 초기 구성 | 생성형 AI 기반 PPT 제작 자동화 요구 |
