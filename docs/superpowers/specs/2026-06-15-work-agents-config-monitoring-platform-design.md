# 업무 에이전트 설정·모니터링 플랫폼 — 설계 문서

- 작성일: 2026-06-15
- 대상 에이전트: `daily-work-reporter`, `weekly-work-reporter`, `pm-board-manager`, `project-wbs-gantt-designer`
- 상태: 설계 확정(브레인스토밍 완료) → 구현 계획 수립 대기

---

## 1. 배경 & 문제 정의

4개 워크플로우 에이전트는 사용자의 업무 데이터를 자동 수집·정리해 일일/주간 보고서, PM 보드, WBS/간트를 생성한다. 자동 수집 자체는 유지하되, 현재 다음 세 가지가 막혀 있다.

1. **(a) 임의 프로젝트 정의 불가** — "프로젝트"가 `daily-work-reporter`의 `git rev-parse --show-toplevel` 폴더 basename에 종속(`daily-work-reporter.md:53, 277-298`). 나머지 셋은 이 인라인 `{폴더명}` 태그를 최우선 상속(`weekly:87`, `pm-board:91`, `wbs-gantt:48`). 즉 **폴더=프로젝트 1:1 가정**이라, 모노레포 1개가 여러 프로젝트를 담으면 하나로 뭉뚱그려지고, 저장소 2개가 한 프로젝트면 둘로 쪼개진다. 사용자가 프로젝트를 선언할 단일 소스가 없다.
2. **(b) 정보 가감 통로 부재** — 4개 전부에 `업무 내용 임의 추가 금지`·`보고서에 없는 업무 창작 금지`(`daily:503`, `weekly:599`, `pm-board:308`) 같은 CRITICAL 제약이 있어, 사용자가 의도적으로 넣고 싶은 include/exclude·가공 규칙을 넣을 "허가된 통로"가 없다.
3. **(c) 웹 모니터링·설정 부재** — 각 에이전트는 *대화형 단발*(호출→질문→초안→확인→저장). 웹에서 보거나 트리거할 표면이 없다. 설정은 산재·암묵적(중앙 config 파일 없음; `pm-board`만 출력 frontmatter에 `config:{정체임계일,WIP임계}`·`milestones:{}` 보유).

### 한 줄 정의
> 폴더명에 묶인 *암묵적* 프로젝트 개념을, 사용자가 웹에서 정의·편집하는 *명시적* 프로젝트 레지스트리 + 수집 가감 규칙으로 바꾸고, 그 설정을 4개 에이전트가 단일 정본으로 참조하게 하며, 실행을 웹에서 모니터링·트리거한다.

### 현황 분석 핵심 발견
- **공통 데이터 모델 이미 존재**: 4개는 같은 work item(제목·쉬운설명·원문기술용어·진행률·카테고리·프로젝트·공수·우선순위·날짜)을 생산/소비한다. 단 "프로젝트"만 누구도 소유하지 않는다.
- **기존 `web-ui`는 "재사용 가능한 껍데기 + 엉뚱한 두뇌"**: `web-ui/`는 전혀 다른 워크플로우(idea-developer, 10개 에이전트)에 연결돼 있고 raw Anthropic API(`claude_client.py`)로 호출하며 **Obsidian MCP가 없다**. 재사용 가능한 것은 배관(WebSocket 이벤트 `broadcast_status/phase/message`, React Flow 워크플로우 시각화, 출력 패널, useWebSocket 훅)뿐. 오케스트레이터·클라이언트·에이전트 두뇌는 우리 4개와 무관.

---

## 2. 확정 결정 (브레인스토밍 산출)

| # | 결정 | 내용 |
|---|---|---|
| ① | 웹 범위 | **B레벨** — 설정 + 실시간 실행 모니터링 + 스케줄 + 웹 승인 |
| ② | 실행 방식 | **헤드리스 Claude Code**(`claude -p` + Obsidian MCP 툴 허용). 4개 에이전트 .md를 단일 진실 소스로 유지, API 재구현 금지 |
| ③ | 순서 | **설정 코어 먼저** — 페인 (a)(b)를 뿌리에서 해결한 뒤 모니터링/스케줄 층을 얹음 |
| ④ | 프로젝트 모델 | **복합형(모노+멀티 혼재)** — 양방향 멤버십 규칙 필요(1폴더→N프로젝트, N폴더→1프로젝트) |
| ⑤ | 승인 게이트 | **에이전트별 차등** — daily/weekly 자동저장+사후검토, pm-board·wbs-gantt 웹 승인 필수 |
| ⑥ | 오케스트레이션 | **하이브리드** — 설정 코어 → n8n 실행/모니터 → (선택) web-ui 졸업 |

---

## 3. 데이터 모델 & 설정 코어

### 3.1 위치 — 단일 정본
- 정본: vault `_config/work-agents.yaml`. 4개 에이전트 모두 이미 Obsidian MCP를 보유 → 새 도구 없이 `obsidian_get_file_contents`로 읽는다.
- 편집 표면(2단계 이후, 선택): Google Sheet는 이 YAML로 **한 방향 동기화**하는 편집 UI일 뿐 정본이 아니다.

### 3.2 스키마 (3층 + 경로 + 어휘)

```yaml
# _config/work-agents.yaml ── 단일 정본
version: 1

paths:                              # 지금 4개 프롬프트에 하드코딩된 경로를 밖으로
  daily_dir: 일일업무보고
  weekly_dir: 주간업무보고
  pm_board: PM보드/PM-Board.md
  wbs_dir: 프로젝트관리

# ── ① 프로젝트 레지스트리 (프로젝트를 1급 객체로) ──
projects:
  - id: atl-rams-ale                # 불변 slug (내부 키)
    name: ATL-RAMS ALE              # 표시명 (차트·보고서 노출)
    aliases: [RAMS, axis-fe, "ATL AXIS Frontend"]   # 모든 철자변형 → 이 id
    status: active                  # active | dormant | done
    deadline: 2026-07-31
    milestones: [{ name: i18n 종료, date: 2026-06-30 }]
  - id: pm-automation
    name: 사내 PM 자동화
    aliases: [pm-agents, custom_subagents]   # 옛 git-basename 태그도 alias로 흡수
    status: active

# ── ② 멤버십 규칙 (복합형: 위→아래 우선순위 매칭) ──
membership:
  - { match: { folder: custom_subagents, path_glob: "agents/rams/**" }, project: atl-rams-ale }  # 1폴더→N분배
  - { match: { jira_prefix: AXIS- }, project: atl-rams-ale }
  - { match: { folder: rams_front }, project: atl-rams-ale }          # N폴더→1접기
  - { match: { folder: custom_subagents }, project: pm-automation }   # 위서 안 잡힌 나머지
  # 매칭 실패 → unassigned (추정 금지 규칙 존중, '미배정'으로 표시해 검토 유도)

# ── ③ 수집 가감 규칙 (글로벌 + 프로젝트별) ──
rules:
  global:
    exclude_commit_prefixes: [chore, build, ci]          # 잡음 커밋 제외
    exclude_path_globs: ["**/node_modules/**"]
    git: { since: midnight, max_count: 50, author: self }
  per_project:
    pm-automation: { always_include: ["주간 회고"], exclude_keywords: ["실험"] }
  thresholds: { stall_days: 3, wip_limit: 8, promise_window: 3 }       # pm-board 값 승격

vocab:                              # 4개 프롬프트에 중복된 사전/분류를 한 곳에서 확장
  glossary_extra: [{ term: ALE, plain: 다국어 지원 라이브러리 }]
  commit_prefix_map: { feat: FEAT, fix: BUG }            # 오버라이드 가능
```

### 3.3 핵심 설계 포인트
1. **`id`(불변) ↔ `name`(표시) ↔ `aliases`(흡수) 3분리** — 매일 철자가 달라도 전부 한 `id`로 정규화. 주간 차트 파편화의 근본 원인 제거.
2. **멤버십 = 우선순위 매칭 리스트** — 복합형 양방향(1폴더→N, N폴더→1)을 위→아래 순서로 해결. `daily`가 태그를 찍는 순간 적용 → 프로젝트가 태어날 때부터 정규화된 `id`로 박힘.
3. **"미배정(unassigned)" 명시** — 기존 `프로젝트명 추정 금지`를 존중하되 조용히 버리지 않고 "미배정"으로 표시 → 사용자가 레지스트리에 추가(가감의 진입점).

---

## 4. 에이전트 통합 & 마이그레이션

### 4.1 공통 읽기 훅 — "Phase 0: 설정 로드 & 프로젝트 해석" (4개 공통)
```
1. obsidian_get_file_contents("_config/work-agents.yaml") 로 정본 로드
   → 파일 없음/파싱 실패 시: 기존 동작(폴더 basename)으로 폴백 (후위호환, 무중단)
2. paths/projects/membership/rules/vocab 파싱
3. 이후 모든 프로젝트 판정 = 멤버십 규칙으로 resolve(id) → 표시는 registry의 name
```

### 4.2 드리프트 방지
- 읽기·해석·가감 알고리즘을 **`agents/_shared/config-contract.md`** 한 파일에 정본화.
- 4개 프롬프트는 동일한 Phase 0 블록 + 이 계약 참조. 수정은 계약 파일 한 곳에서.
- 4개를 **lockstep**으로 한 번에 수정(특히 `{폴더명}` 규칙 자체가 없는 `pm-board` 포함).

### 4.3 에이전트별 변경점

| 에이전트 | 지금 | 바뀌는 것 |
|---|---|---|
| **daily** | git 폴더 basename → `{폴더명}` 자동 부착 (`:52-56, 277-298`) | 멤버십 규칙으로 `id` 해석 → 표시명 `{name}` 부착. git 로그에 글로벌 가감 적용. 실패 시 `{미배정}` |
| **weekly** | 5단계 프로젝트 추론 cascade (`:86-91`) | cascade 맨 위에 "0단계: registry 정규화" 추가(alias→id 흡수). 차트 라벨=registry `name`(파편화 종결). per-project 가감 + thresholds |
| **pm-board** | `{폴더명}` 규칙 자체가 없음 | 규칙 신규 도입 + 포트폴리오 `id` 기준 집계. 마일스톤·마감 registry 우선. thresholds를 config에서(보드 frontmatter보다 우선) |
| **wbs-gantt** | 프로젝트명=자유 텍스트, 목표/마감 2~3개 질문 | 입력 프로젝트명 registry 검증 + `deadline`/`milestones` 자동 주입(scope 질문 감소). 멤버십으로 소속 항목 선별 |

### 4.4 인라인 태그 표기 방식 (확정)
- **표시명 `{name}`**으로 찍고, 모든 소비자는 registry로 `name`/`alias` → `id` 정규화. (가독성 우선. registry가 정본이라 정규화가 이제 신뢰 가능)

### 4.5 마이그레이션 — "재작성 없이 alias 흡수"
- 과거 보고서 파일은 **절대 무수정**. 옛 폴더명(`custom_subagents` 등)을 registry `aliases`에 한 줄 추가하면 weekly/pm/wbs가 옛 태그를 자동으로 새 `id`로 정규화.
- 마이그레이션 = 옛 폴더명을 alias 목록에 추가하는 것. (선택적 일괄 치환 스크립트 가능하나 불필요)

### 4.6 후위호환 3중 폴백
1. config 파일 없음 → 기존 폴더-basename 동작 그대로
2. 프로젝트 해석 실패 → `{미배정}` 표시(조용히 버리지 않음, 추정도 안 함)
3. 옛 보고서의 옛 태그 → alias 흡수(혼재 상태 정상 동작)

---

## 5. n8n 오케스트레이션 (Phase 2)

### 5.1 핵심 — "전 에이전트 draft-only 파이프라인"
헤드리스 Claude Code는 호출마다 무상태라 "초안 만들고 멈췄다 승인 후 저장"을 한 세션에서 못 한다. → **실행과 저장 분리**:
- 모든 에이전트를 `--draft-only` 모드로 실행 → Obsidian을 읽고 분석해 완성된 markdown 초안을 *반환만* 함(저장 안 함).
- 저장은 n8n이 Obsidian REST로 결정적 기록(이미 완성된 markdown → LLM 재실행 불필요).
- 차등 승인 = 이 사이에 Wait 노드를 끼우냐 마냐의 차이. 통일 파이프라인 + 균일 telemetry + 단일 쓰기 경로.
- 에이전트 프롬프트엔 "Phase 4 저장"에 draft-only 분기만 추가(지시문/환경변수 1줄). 기존 대화형 동작 보존.

### 5.2 균일 파이프라인
```
[트리거: cron 또는 수동/webhook]
  → ① config 검증        (YAML 스키마 검증 — 깨지면 중단+알림)
  → ② 헤드리스 실행       (claude -p --agent X --draft-only → 초안 markdown 반환)
  → ③ 승인 필요?
       ├─ 아니오(daily/weekly) ───────────────→ ⑤ 쓰기
       └─ 예(pm·wbs) → ④ Wait-webhook 승인
                         (초안 뷰어에서 승인/수정/거부)
                         승인·수정 → ⑤ 쓰기  /  거부 → 종료+로그
  → ⑤ Obsidian REST 쓰기  (승인된 markdown 결정적 기록)
  → ⑥ 실행 로그 + 요약 알림 (저장 경로 · 미배정 항목 · KPI 1줄)
```

### 5.3 스케줄 기본값 (조정 가능 + 수동 트리거 항상 가능)

| 에이전트 | 기본 스케줄 | 승인 | 비고 |
|---|---|---|---|
| `daily` | 평일 18:30 | 자동저장 | 입력 없으면 git/obsidian만으로 초안 |
| `weekly` | 금 17:00 | 자동저장 | 그 주 일일보고 집계 |
| `pm-board` | 평일 08:30 | 웹 승인 | 판단(약속·정체·리스크) 검토 필요 |
| `wbs-gantt` | 온디맨드 | 웹 승인 | 프로젝트·마감 지정(수동) |

### 5.4 모니터링
- n8n 실행뷰가 곧 모니터(이력·노드 상태·로그·재시도 기본 제공).
- 감사 로그: 매 실행을 vault `_runs/YYYY-MM-DD-{agent}.json`에 1건(시작·소요·저장경로·미배정 목록·KPI) → 3단계 web-ui가 그대로 읽어 졸업.

### 5.5 승인 뷰어 (최소 구현 → 3단계 씨앗)
- n8n Wait-webhook + 작은 정적 초안 뷰어(markdown+Mermaid 렌더 + 승인/수정/거부). n8n 내 Mermaid 렌더 어색함을 이 뷰어가 해결.

### 5.6 에러 처리 & 보안
- Obsidian 오프라인/쓰기 실패 → n8n 재시도 + PushNotification, 초안은 `_runs/`에 보존.
- config 깨짐 → 에이전트 실행 *전* 검증 노드에서 차단(잘못된 설정의 4개 동시 오염 방지).
- 헤드리스 권한 → `--dangerously-skip-permissions` 대신 스코프 allowlist(Obsidian MCP + Bash + git). API 키는 n8n 자격증명 금고. 런어웨이 가드(max turns).
- 미배정 항목 → 실행 요약 노출 → registry에 alias/프로젝트 추가(가감 루프 완성).

---

## 6. 단계별 로드맵

### Phase 1 — 설정 코어 (페인 a·b 근본 해결)
1. `_config/work-agents.yaml` 정본 작성(실제 프로젝트 + 멤버십 + 규칙)
2. `agents/_shared/config-contract.md` 작성(읽기·해석·가감 알고리즘 정본)
3. 4개 에이전트 .md에 "Phase 0" 블록 추가(lockstep)
4. daily 폴더캡처→멤버십 해석 교체; weekly 0단계 정규화; pm-board 규칙 신규; wbs-gantt registry 검증
5. 마이그레이션: 옛 폴더명 alias 등록
- **완료 기준**: config만 있으면 4개 에이전트가 대화형에서도 사용자 정의 프로젝트·가감 준수(n8n 없이 즉시 유용).

### Phase 2 — n8n 운영층 (페인 c)
1. 에이전트 프롬프트에 `--draft-only` 분기 추가
2. config 검증 노드 + 4개 균일 n8n 워크플로우
3. 스케줄(cron) + 수동 트리거(webhook)
4. 차등 승인(Wait-webhook) + 최소 초안 뷰어
5. Obsidian REST 쓰기 + `_runs/` 감사 로그 + 알림
- **완료 기준**: 무인 실행·스케줄·차등 승인·n8n 모니터링 작동.

### Phase 3 (선택) — web-ui 졸업
- 조건: n8n 범용 UI가 실제로 부족할 때만.
- web-ui 껍데기(WebSocket/React Flow/출력패널) 재활용, 두뇌만 4-에이전트 오케스트레이터로 교체, `_runs/`+config 읽는 전용 포트폴리오 대시보드(라이브 telemetry + 초안 승인).
- **완료 기준**: 한 앱에서 설정·실행·모니터·승인·포트폴리오.

---

## 7. 리스크 & 완화

| 리스크 | 완화 |
|---|---|
| 헤드리스가 안전게이트 깸 | draft-only 분리 + 차등 승인(pm·wbs 필수) + `_runs/` 초안 보존 |
| config-프롬프트 드리프트 | `config-contract.md` 단일 정본 + 4개 lockstep + 후위호환 폴백 |
| 정본 이중화(YAML↔Sheet) | YAML 정본, Sheet는 한 방향 동기화 + 검증 노드 |
| 백필 부채 | 옛 폴더명 alias 흡수(과거 파일 무수정) |
| Windows+localhost 결합 | n8n 동일 머신 구동(Obsidian REST·git·python 동거) |
| 헤드리스 권한/시크릿 | 스코프 allowlist(no skip-permissions) + 자격증명 금고 + max-turns |
| web-ui 스코프 크리프 | 3단계 조건부로 미룸(n8n로 모델 검증 후에만) |
| 휴리스틱 잔존(동일항목 매칭) | config는 *어느 프로젝트*만 고침; 동일항목 매칭 오류는 별도 — 승인·검토·사후 Obsidian 수정으로 커버 |

---

## 8. 테스트 전략
- **Phase 1**: 골든 픽스처(샘플 일일보고 세트 + 샘플 config) → 4개 에이전트 출력의 프로젝트 정규화/가감 결과를 기대값과 대조. 특히 ①복합형 양방향 매핑 ②옛 태그 alias 흡수 ③미배정 처리 ④config 없을 때 폴백.
- **Phase 2**: n8n 워크플로우 dry-run — draft-only 출력이 저장과 분리되는지, 승인 분기(daily 자동 vs pm 대기), config 깨짐 차단, Obsidian 오프라인 재시도.
- **회귀**: 기존 대화형 호출 무중단(후위호환) — config 유무 양쪽.

---

## 9. 미해결 입력 (구현 시 확보)
- **실제 프로젝트 목록** — Phase 1 빌드 시점에 사용자로부터 확보(표시명·관련 폴더/저장소·별칭·마감/상태). 설계는 복합형 기준으로 완결돼 있어 이 입력만 채우면 `_config/work-agents.yaml` 작성 가능.
- 스케줄 시간대 미세 조정(사용자 실제 업무 리듬 반영).
- 헤드리스 Claude Code CLI의 정확한 호출 형태(`--allowedTools`/settings 방식) — Phase 2 착수 시 환경 검증.
```
