# 업무 에이전트 설정 계약 (config-contract)

daily-work-reporter · weekly-work-reporter · pm-board-manager · project-wbs-gantt-designer 4개
에이전트가 공유하는 설정 로드·프로젝트 해석·수집 가감 알고리즘의 **단일 정본**이다.
Phase 0 블록이나 이 알고리즘을 수정할 때는 4개 프롬프트와 이 문서를 **lockstep**으로 함께 갱신한다.
설계 배경: `docs/superpowers/specs/2026-06-15-work-agents-config-monitoring-platform-design.md`

## 1. 정본 위치와 로드

- 정본: Obsidian vault **`_config/work-agents.yaml`** (리포 원본: `agents/_shared/work-agents.sample.yaml`)
- 로드: `mcp__obsidian__obsidian_get_file_contents("_config/work-agents.yaml")`
- **실패 시(404/연결 오류/YAML 파싱 불가): Phase 0 전체를 조용히 생략하고 기존 동작 유지.**
  에러 메시지를 사용자에게 보이지 않는다 (config 없는 환경 = 정상 동작 환경).

## 2. 스키마 (version: 1)

| 키 | 내용 | 소비자 |
|---|---|---|
| `paths.daily_dir/weekly_dir/pm_board/wbs_dir` | 프롬프트 하드코딩 경로의 오버라이드 (없는 키는 기존 기본값) (오버라이드는 프롬프트 본문 전체의 하드코딩 경로에 적용) | 4개 전부 |
| `projects[]: {id, name, aliases[], status, deadline?, milestones?}` | 프로젝트 레지스트리. id=불변 내부 키(그룹핑), name=표시명(태그·차트·보드 노출), aliases=모든 철자변형 | 4개 전부 |
| `membership[]: {match: {folder?|path_glob?|jira_prefix?}, project: <id>}` | 폴더/경로/식별자 → 프로젝트 매칭 규칙, **위→아래 첫 매칭 승리** | daily(태깅 시) |
| `rules.global.exclude_commit_prefixes[]` | git 수집에서 제외할 커밋 prefix | daily |
| `rules.global.git: {since, max_count}` | git log 수집 파라미터 | daily |
| `rules.per_project.<id>: {exclude_keywords[]?, always_include[]?}` | 프로젝트별 가감: exclude_keywords=제목·기술용어에 키워드 포함 항목을 집계에서 제외, always_include=제외 규칙보다 우선(절대 제외 금지) | weekly(스크립트) |
| `rules.thresholds: {stall_days, wip_limit, promise_window}` | 정체임계일 / WIP임계 / 약속 미이행 판정 영업일 — **보드 frontmatter 값보다 우선** | pm-board |
| `vocab.glossary_extra[]: {term, plain}` | 기술 용어 변환 사전 확장 | daily, weekly |
| `vocab.commit_prefix_map: {prefix: TAG}` | 커밋 prefix→카테고리 매핑 오버라이드 | daily |

## 3. 프로젝트 해석 알고리즘 — resolve(원시값)

정규화 규칙: **소문자화 + 공백·구두점(`. , : ; - _ ( ) [ ] { } ·`) 제거**
(aggregate_weekly.py의 `normalize_key()`와 동일해야 한다)

1. **멤버십 매칭** (원시값이 폴더명/경로/식별자일 때): `membership` 목록을 위→아래로 순회,
   `folder`(정규화 일치) / `jira_prefix`(식별자 접두 일치) / `path_glob`(경로를 알 때만) 첫 매칭의 `project`(id) 채택
2. **레지스트리 전역 검색** (원시값이 태그/이름일 때 또는 1 실패 시): 모든 프로젝트의
   `id`/`name`/`aliases`를 정규화하여 일치 검색 → 매칭 프로젝트 채택
3. **실패 → 미배정**: 임의로 프로젝트명을 만들지 않는다 (기존 "추정 금지" 원칙).
   daily는 `{미배정}` 태그를 부착하고, 실행 요약에서 사용자에게 레지스트리 추가를 안내한다.

**표시 vs 내부 키**: 노출(인라인 태그·차트 라벨·보드 표)은 항상 `name`, 그룹핑·rules 참조는 `id`.

**3가지 상태 구분** (혼동 금지):
- `일반 업무`: 프로젝트 정보 자체가 없는 항목 (config 이전부터 있던 기존 폴백 — 유지)
- `미배정`: daily가 폴더를 캡처했으나 membership/레지스트리 매칭 실패 (config 있을 때만 발생)
- `미등록(unregistered)`: weekly 집계에서 인라인 태그가 있으나 레지스트리에 없음 —
  **원시 태그를 그대로 유지**하고 `meta.unregistered_projects`로 보고 (사용자가 alias를 추가할 수 있도록
  원시 철자를 보존; 미배정으로 뭉개지 않는다)

- **`미배정` 특례**: 스크립트·소비자는 `{미배정}` 태그를 미등록(unregistered)으로 보고하지 않는다 — 그룹으로는 유지하되 레지스트리 추가 안내 대상에서 제외 (해석 실패 마커이지 프로젝트명이 아님)
- **`path_glob` 미적용(Phase 1 디스코프)**: 현행 에이전트는 항목 단위 경로 정보를 갖지 않아 membership의 `path_glob` 규칙을 적용하지 않는다 (folder/jira_prefix만 유효). 모노레포 1폴더→N프로젝트 분배가 필요해지면 후속 단계에서 활성화

## 4. 에이전트별 적용 지점

| 에이전트 | Phase 0 이후 바뀌는 것 |
|---|---|
| daily | 캡처한 폴더 basename을 `resolve()` → `{name}` 부착(실패 시 `{미배정}`). git log에 `exclude_commit_prefixes`·`git.since/max_count` 적용, `commit_prefix_map` 오버라이드, `glossary_extra` 사전 확장 |
| weekly | 그룹핑 cascade 최상단 "0단계: registry 정규화". 스크립트 핸드오프(§5)로 수치 레벨 정규화·가감. 차트 라벨 = `name`. `meta.unregistered_projects`를 보강 제안에 노출 |
| pm-board | `thresholds`를 정체임계일/WIP임계/약속판정에 사용(보드 frontmatter보다 우선). 포트폴리오를 id 기준 집계·`name` 표시. 마일스톤·마감은 registry `projects[].milestones/deadline` 우선 |
| wbs-gantt | 입력 프로젝트명을 `resolve()`로 검증(미등록이면 사용자 확인 후 자유 텍스트 진행). registry `deadline`/`milestones` 자동 주입(질문 생략). 보고서 항목 선별에 인라인 태그 resolve 추가 |

## 5. 스크립트 핸드오프 (weekly → aggregate_weekly.py)

스크립트는 YAML을 파싱하지 않는다. weekly 에이전트가:
1. 읽은 YAML을 **구조 그대로**(키·값 무변형, 표기만 JSON) canonical JSON으로 직렬화
2. 임시 디렉토리에 `work-agents.json`으로 저장
3. `--config <경로>`로 전달

스크립트는 JSON 스키마(최소: `projects` 배열)를 검증하고, 실패 시 **config를 무시**하고
기존 동작 + `meta.config_loaded: false`. 스크립트가 소비하는 키는 `projects[]`(정규화)와
`rules.per_project`(exclude_keywords/always_include)뿐이다 — membership(폴더 기반)은 태깅
시점(daily) 정보라 스크립트에서 적용하지 않는다.

## 6. 마이그레이션

과거 보고서는 절대 수정하지 않는다. 옛 폴더명 태그(`{custom_subagents}` 등)는 레지스트리
`aliases`에 한 줄 추가하는 것으로 흡수된다 (예: `pm-automation.aliases: [custom_subagents]`).

membership의 `folder` 값은 반드시 해당 프로젝트의 `aliases`에도 등재한다 — weekly 스크립트·pm-board·wbs는 membership을 보지 않고 레지스트리(aliases)로만 정규화하므로, 누락 시 daily에서만 해석되고 하류에서 미등록으로 표시된다.
