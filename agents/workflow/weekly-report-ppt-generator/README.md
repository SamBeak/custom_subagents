# weekly-report-ppt-generator

> Obsidian 주간업무보고 Markdown 노트를 레퍼런스 디자인의 PowerPoint(.pptx)로 변환하는 워크플로우 에이전트

## 개요

기존 `weekly-work-reporter` 에이전트가 생성한 `주간업무보고/YYYY-MM-DD~YYYY-MM-DD.md`를 입력으로 받아, `docs/1_ref/[보고]-연구개발팀 일일업무보고_백현규_4m2w.pptx`와 동일한 디자인의 `.pptx` 파일을 자동 생성합니다.

- **표지·요약 고정 슬라이드**: 레퍼런스 PPT 복사 + run 단위 플레이스홀더 치환
- **프로젝트·WBS·다음주 슬라이드**: 블록 템플릿(`blocks.pptx`) 동적 복제 (`copy.deepcopy` + `_sldIdLst`)
- **한글 폰트**: 맑은 고딕 + 나눔스퀘어 네오 Heavy (East Asian typeface 이중 주입)
- **Office 강조색**: `#4472C4` 파랑 중심

## 아키텍처

```
~/.claude/
├── agents/
│   └── weekly-report-ppt-generator.md      [에이전트 정의]
└── skills/
    └── weekly-report-ppt-builder/          [전용 스킬]
        ├── SKILL.md
        ├── scripts/
        │   ├── build_pptx.py               메인 엔트리
        │   ├── parse_note.py               Markdown 파서
        │   ├── plan_slides.py              슬라이드 플랜
        │   ├── pptx_ops.py                 치환/복제 유틸
        │   └── validate_output.py          생성 파일 검증
        ├── assets/
        │   ├── reference.pptx              플레이스홀더 주입된 레퍼런스
        │   └── blocks.pptx                 차트/SmartArt 제거한 블록
        └── references/
            ├── slide-map.yaml              슬라이드별 치환 키·좌표
            ├── section-rules.md            섹션 → 슬라이드 매핑 규칙
            └── pptx-pitfalls.md            python-pptx 함정 카탈로그
```

## 워크플로우 (Phase 0~5)

| Phase | 이름 | 핵심 동작 |
|-------|------|----------|
| 0 | 사전 점검 | python-pptx 확인, assets 존재 확인, 쓰기 권한 확인 |
| 1 | 입력 확정 | 주차 계산, Obsidian 노트 읽기 |
| 2 | 노트 파싱 | `parse_note.py` → `sections.json` |
| 3 | 슬라이드 플랜 + **사용자 승인** | `plan_slides.py` → `slide_plan.json` |
| 4a | 고정 슬라이드 치환 | `reference.pptx` 복사 + 표지/요약 치환 |
| 4b | 블록 동적 삽입 | `blocks.pptx`에서 deepcopy로 슬라이드 복제 |
| 5 | 검증 및 저장 | ZIP 무결성 확인 + vault에 `.pptx` 저장 |

## 섹션 → 슬라이드 매핑

| 노트 섹션 | 슬라이드 유형 | 소스 |
|---|---|---|
| `## 요약` / `## Executive Summary` | 요약 (1장) | reference |
| `## {ProjectName}` | 프로젝트 업무 테이블 (N장) | block 복제 |
| `## {WBS제목}` | WBS 세트 (1~3장) | block 복제 |
| `## 다음 주 계획` | 다음주 계획 (1장) | block |
| `## 주간 통계` | 요약 슬라이드에 병합 | 추가 없음 |

## python-pptx 함정 카탈로그 (10종)

1. Slide duplicate 안티패턴 (차트/SmartArt rId 꼬임)
2. Run 단위 치환 (paragraph.text 금지)
3. 한글 폰트 이중 주입 (font.name + XML East Asian typeface)
4. Windows 경로 (pathlib + subprocess 따옴표)
5. 셀 병합된 표 (좌상단 셀에만 쓰기)
6. Picture/아이콘 제외 (run.text 있는 shape만)
7. 바이너리 저장 (Obsidian MCP 불가, 파일시스템 직접 쓰기)
8. 파일 잠금 (PermissionError 시 PowerPoint 종료 안내)
9. 진행률 포맷 (`100/100%` → 숫자 추출 후 재조립)
10. python-pptx 미설치 (import 검사 + pip 안내)

## 호출 예시

```
✅ "이번 주 주간업무보고 PPT 만들어줘"
✅ "주간보고서 ppt로 변환해줘"
✅ "주간업무보고/2026-04-10~2026-04-13.md를 PPT로"
❌ "일일업무보고 PPT 만들어줘"        → daily-work-reporter 호출
❌ "주간업무보고 작성해줘"             → weekly-work-reporter 호출
❌ "PPT 템플릿 디자인해줘"             → 일반 요청
```

## 의존성

- Python >= 3.9
- python-pptx >= 0.6.21
- PyYAML
- Obsidian MCP (`mcp__obsidian__*`)
- 선행 에이전트: `weekly-work-reporter` (주간 Markdown 노트 생성)
- 전용 스킬: `weekly-report-ppt-builder`

## 출력

- **경로**: `{vault_root}/주간업무보고/YYYY-MM-DD~YYYY-MM-DD.pptx`
- **슬라이드 구성**: 표지 1 / 요약 1 / 프로젝트 M / WBS K / 다음주 1
- **완료 리포트**: 저장 경로 + 슬라이드 수 + 주요 치환 내역 샘플 3건

## 설계 참조

- `C:\Users\ATL\.claude\plans\rustling-squishing-pumpkin.md` — 원본 설계 플랜
- `일일업무보고/2026-04-16.md` — 설계 완료 기록

## 변경 이력

| 날짜 | 변경 | 사유 |
|------|------|------|
| 2026-04-16 | 초기 설계 (Obsidian 일일보고) | 주간업무보고 PPT 자동 생성 요구 |
| 2026-04-20 | 에이전트 정의 파일 커밋 | 04/16 설계안 기반 구현 착수 |
