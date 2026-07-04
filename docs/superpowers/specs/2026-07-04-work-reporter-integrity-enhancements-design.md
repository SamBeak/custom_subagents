# 일일·주간 업무보고 에이전트 정합성 고도화 (A안) — 설계 문서

- 작성일: 2026-07-04
- 대상 에이전트: `daily-work-reporter`, `weekly-work-reporter`
- 관련 자산: `scripts/`(리포 루트), `~/.claude/agents/`(배포본), `~/.claude/commands/일일마감.md·주간마감.md`, zero-touch 캐스케이드
- 상태: 설계 확정 → 구현 진행
- 선행 관계: `2026-06-15-work-agents-config-monitoring-platform-design.md`(설정 코어 플랫폼)의 **선행 단계**. 본 설계(A안)는 인프라 추가 없이 정합성·신뢰도를 확보하며, A-1(배포 동기화)과 A-2(결정적 집계)는 플랫폼 Phase 1의 전제가 된다.

---

## 1. 배경 & 문제 정의

리포의 daily v1.2.0 / weekly v1.3.0은 프로젝트 태그·메타데이터·차트 4종·공수 산정까지 갖췄으나, 실제 운영에서 다음 네 가지 정합성 문제가 확인되었다.

1. **(A-1) 배포 드리프트** — 운영 실행 경로(주간마감 캐스케이드, zero-touch)는 `~/.claude/agents/*.md`를 읽는데, 이 배포본이 구버전이다(daily: 프로젝트 태그·메타데이터 규칙 부재, 164줄 차이 / weekly: 차트·공수 로직 전무, 298줄 차이). 기존 `scripts/install-agent.ps1`은 대화형(Read-Host)이고 대상이 **프로젝트 로컬** `.claude/agents`라서 이 문제를 해결하지 못한다. 드리프트를 감지·해소하는 비대화형 도구가 없다.
2. **(A-2) 집계의 LLM 산술 의존** — weekly의 파싱·공수 점수·정규화·차트 데이터 산정(Phase 7-1~7-4)을 LLM이 암산한다. 합계 100% 보장, 진행률 델타, 일자별 카운트가 실행마다 달라질 수 있고 검증 불가능하다.
3. **(A-3) 날짜 축 연속성 부재** — daily는 오늘 보고서만 본다(어제의 "내일 할 일"이 자동으로 이어지지 않고, 진행률 연속성도 없음). weekly는 해당 주 파일만 읽어 "신규 착수 vs 이월" 구분이 사실상 추정이다.
4. **(A-4) 마감 체계와 미연동** — `일일마감`이 부여하는 frontmatter `status: confirmed`를 두 에이전트 모두 인식하지 못한다(확정 보고서를 경고 없이 수정 가능, 주간 통계에 확정/미확정 구분 없음). 또한 `일일마감`/`주간마감` 커맨드가 `~/.claude/commands/`에만 존재해 리포(배포 컬렉션)가 이 자산을 관리하지 못한다.

## 2. 확정 결정

| # | 결정 | 내용 |
|---|---|---|
| ① | 범위 | A안 4종(A-1~A-4)만. 설정 코어(프로젝트 레지스트리)·n8n·web은 후속(별도 spec 존재) |
| ② | 배포 대상 | 사용자 스코프 `~/.claude/agents`(캐스케이드가 읽는 경로). 프로젝트 스코프는 비대상 |
| ③ | 집계 스크립트 | Python 표준 라이브러리만 사용(무의존성), 에이전트 로컬 번들(`agents/workflow/weekly-work-reporter/scripts/`) — gov-docx 선례 준수 |
| ④ | 스크립트 런타임 경로 | sync 스크립트가 `~/.claude/agent-scripts/<agent-name>/`로 스크립트까지 배포. 프롬프트는 배포 경로 → 리포 경로 → 인라인 휴리스틱 순 폴백 |
| ⑤ | 차트 수치의 정본 | 스크립트 실행 성공 시 차트 블록(Mermaid/표)은 스크립트 출력 **그대로 사용**(LLM 재계산 금지). 실패 시 기존 인라인 휴리스틱 폴백 |
| ⑥ | 후위호환 | 모든 변경은 기존 대화형 동작 무중단. 신규 입력(전일/전주/스크립트)이 없어도 기존과 동일하게 동작 |
| ⑦ | 임의 추가 금지 원칙 유지 | 전일 이월 항목은 **사용자 확인 후에만** 포함(기존 Obsidian recent-changes 패턴과 동일) |

---

## 3. A-1 — 배포 동기화: `scripts/sync-agents.ps1` (신규)

### 3.1 목적
리포(정본) ↔ 배포본(`~/.claude/agents`, `~/.claude/commands`, `~/.claude/agent-scripts`) 간 드리프트를 **비대화형으로 감지·해소**한다. 기존 `install-agent.ps1`은 유지(대화형 첫 설치용)하되, 운영 동기화는 이 스크립트가 담당한다.

### 3.2 인터페이스

```powershell
pwsh scripts/sync-agents.ps1                 # 드리프트 리포트만 (기본, 무변경)
pwsh scripts/sync-agents.ps1 -Apply          # 이미 배포된 항목 중 다른 것만 갱신
pwsh scripts/sync-agents.ps1 -Apply -All     # 미배포 에이전트/커맨드도 신규 설치
pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter -Apply
pwsh scripts/sync-agents.ps1 -Dest <path>    # 기본값: $HOME\.claude
```

### 3.3 동작 명세
- **대상 산출**: `agents/{category}/{name}/{name}.md`(agent.json 존재하는 디렉토리) 전수 + `commands/*.md`(리포에 존재 시) + 각 에이전트의 `scripts/*`(존재 시).
- **비교**: SHA256 해시(`Get-FileHash`). 배포본은 리포 파일과 **바이트 동일 사본**(변형·스탬프 없음 — 해시 비교 단순성 유지).
- **리포트**: 이름 / 종류(agent·command·script) / 리포 버전(agent.json `version`) / 상태(`IDENTICAL`·`DIFFERENT`·`NOT_DEPLOYED`) 표 출력. 종료 코드: 전부 IDENTICAL이면 0, 드리프트 존재 시 1 (자동화 체크 활용).
- **Apply 규칙**:
  - 기본: 상태 `DIFFERENT`인 항목만 리포 → 배포로 복사(업데이트).
  - `-All`: `NOT_DEPLOYED` 항목도 설치.
  - 에이전트 스크립트는 `~/.claude/agent-scripts/<agent-name>/`로 복사(해당 에이전트가 sync 대상일 때 함께).
  - **배포 디렉토리에만 존재하는 파일(리포 무대응)은 절대 건드리지 않는다** (예: `figma-prompt-generator.md` 등 리포 외 자산).
- **필터 범위**: `-Agent`는 에이전트(및 그 스크립트)에만 적용. `commands/*.md`는 필터와 무관하게 항상 리포트에 포함되며 Apply 규칙(DIFFERENT만, `-All` 시 신규 포함)을 동일하게 따른다.
- **비대화형**: `Read-Host`·확인 프롬프트 없음. 출력은 요약 표 + 변경 목록.
- 에러: 대상 디렉토리 생성 실패·복사 실패 시 해당 항목만 FAIL로 표기하고 계속, 종료 코드 1.

### 3.4 문서
- 루트 `README.md` 설치 안내에 sync 스크립트 사용법 1문단 추가.

---

## 4. A-2 — 주간 집계 결정화: `aggregate_weekly.py` (신규)

### 4.1 위치·의존성
- `agents/workflow/weekly-work-reporter/scripts/aggregate_weekly.py`
- Python 3.9+ 표준 라이브러리만 사용(외부 패키지 금지 — frontmatter는 정규식 파싱).
- 테스트: 같은 디렉토리 `test_aggregate_weekly.py` + `fixtures/`(pytest 기반, `python -m pytest`로 실행 가능해야 함).

### 4.2 CLI

```
python aggregate_weekly.py --dir <daily_md_dir>
    [--week-start YYYY-MM-DD] [--week-end YYYY-MM-DD]
    [--prev-weekly <prev_weekly.md>]
    [--include-weekends]
    [--out <result.json>]        # 미지정 시 stdout
```

- `--dir`: `YYYY-MM-DD.md` 형식 파일들이 들어있는 디렉토리. **에이전트가 Obsidian MCP로 읽은 내용을 스크래치 임시 디렉토리에 저장한 것**(스크립트가 볼트를 직접 읽지 않음 — 볼트 경로 비의존).
- 날짜 범위 필터 + 주말 제외(기본). JSON은 UTF-8, `ensure_ascii=False`.

### 4.3 파싱 명세 (프롬프트 규칙의 결정적 구현)

- **frontmatter**: 첫 `---` 쌍 내부의 `key: value` 라인에서 `date`, `status`, `total_hours`, `focus_project` 추출.
- **섹션**: H2 `오늘 한 일`·`진행 중인 일`·`내일 할 일`·`특이사항`은 카테고리 섹션. 그 외 H2는 프로젝트 헤더로 간주(하위 항목의 기본 프로젝트).
- **항목 라인**: `- **...**`로 시작하는 최상위 불릿. 제목부에서 선행 `[FEAT|BUG|REFACTOR|OPS|DOC|QA]` 태그 분리. 제목 뒤 backtick 토큰들을 **순서 무관·부분 존재 허용**으로 해석:
  - 진행률 `` `N/100%` ``
  - 프로젝트 `` `{이름}` ``
  - 공수 `` `(N h|N d)` `` (예: `(2h)`, `(0.5d)`; `1d = 8h` 환산)
  - 우선순위 `` `[P0|P1|P2|Critical|Major|Minor]` ``
- **하위 불릿**: 개수(복잡도 가중치용), 식별자 라인(`(PR #.., JIRA: .., 이슈 ..)` 패턴), 마지막 괄호 라인 = 원문 기술 용어.
- **프로젝트 판정 우선순위**(weekly 프롬프트와 동일): 인라인 `{태그}` → 프로젝트 H2 → frontmatter `project` → 판정 불가 시 `"일반 업무"`.
- **카테고리 판정**: 명시 태그 우선, 부재 시 프롬프트 7-2의 키워드 휴리스틱을 동일 키워드 목록으로 구현.
- 파싱 불가 항목: `unparsed` 배열에 원문 보존(누락 금지), 통계에서 제외하되 개수는 meta에 보고.

### 4.4 집계 명세

- **동일 업무 병합 키**: 정규화(소문자·공백·구두점 제거)한 원문 기술 용어, 부재 시 정규화 제목. 키가 같으면 여러 날 등장을 1건으로 병합(시작 진행률 = 최초 등장일 값, 최종 = 최종 등장일 값). *의미상 유사(철자 상이) 병합은 스크립트가 하지 않는다* — 잔여 의미 병합은 LLM이 서술에서만 보정하고 **수치는 스크립트 값을 유지**(캡션에 산정 기준 명시).
- **처리 건수 정의**: 일자별 처리 건수 = 그 날의 "오늘 한 일" + "진행 중인 일" 항목 수. "내일 할 일"·"특이사항"은 공수·처리량 집계에서 제외("내일 할 일"은 다음 주 계획 소스로만 별도 수집).
- **공수 점수**: weekly 프롬프트 7-1과 동일 — 시간 명시 항목은 시간 합산(1d=8h), 미명시 항목은 휴리스틱(기본 1.0 + 진행률 델타 + `min(하위불릿×0.2, 1.0)` + 키워드 가중 최대 1.5 + 다일 등장 `0.3×(N-1)` 최대 1.5). 혼합 허용.
  - 진행률 델타의 단일 등장 항목 처리: **1일만 등장한 항목은 시작값 0으로 간주해 델타 = 최종값/100** (프롬프트 예시 "100/100% 단일일 = +1.0"의 일반화 — 단일일 70%면 +0.7).
- **정규화**: 프로젝트·카테고리 비율 정수 반올림 후 **최대 그룹이 잔차 흡수해 합계 정확히 100**. 5% 미만 그룹은 "기타" 통합(단일 통합 그룹이 5% 미만이면 유지).
- **완료 판정**: 최종 진행률 100% → 완료. 완료율 = 완료/(완료+진행중), 10% 반올림.
- **이월 판정**(`--prev-weekly` 지정 시): 전주 주간보고의 "진행 중"(프로젝트 하위 H4)·"다음 주 계획" 섹션 항목에서 병합 키 집합을 만들고, 이번 주 병합 항목의 `carryover` = 키 존재 여부. 전주 파일 미지정/파싱 실패 시 `carryover: null`·`stats.carried_in: null`(추정 금지).
- **전주 대비(WoW)**: 전주 주간보고의 "주간 통계" 섹션에서 `완료 업무: N건` 등 수치를 파싱해 `stats.prev_week`에 담고 델타 계산. 파싱 실패 시 null.

### 4.5 출력 JSON 스키마 (top-level)

```json
{
  "meta":   { "week_start": "", "week_end": "", "iso_week": "YYYY-WNN",
              "analyzed_dates": [], "missing_weekdays": [],
              "confirmed_dates": [], "draft_dates": [], "unparsed_count": 0 },
  "days":   [ { "date": "", "weekday_kr": "월", "item_count": 0, "completed_count": 0, "status": "confirmed|draft|none" } ],
  "merged": [ { "key": "", "title": "", "tech_term": "", "project": "", "category": "FEAT",
                "first_date": "", "last_date": "", "days_seen": 1,
                "start_pct": 0, "end_pct": 100, "completed": true,
                "hours_total": null, "priority": null, "identifiers": [],
                "carryover": null, "last_section": "오늘 한 일" } ],
  "tomorrow_plans": [ { "date": "", "title": "", "project": "", "category": "" } ],
  "projects":   [ { "name": "", "effort_score": 0.0, "effort_pct": 0, "done_count": 0,
                    "wip_count": 0, "completion_pct": 0, "bar": "▓▓▓░░░░░░░" } ],
  "categories": [ { "tag": "FEAT", "label_kr": "신규 개발", "pct": 0, "count": 0 } ],
  "charts": { "project_pie": "```mermaid\npie showData title ...\n```",
              "category_pie": "```mermaid\n...\n```",
              "daily_trend_table": "| 날짜 | 요일 | 처리 건수 | 시각화 |\n|...",
              "completion_table": "| 프로젝트 | 완료 | 진행 중 | 완료율 시각화 |\n|..." },
  "stats":  { "done": 0, "wip": 0, "new_started": 0, "carried_in": null, "carry_next": 0,
              "confirmed_reports": 0, "total_reports": 0,
              "prev_week": { "done": 0, "wow_done_delta": 0 } }
}
```

`charts.*`는 **완성된 마크다운 블록**(펜스 포함)으로, 에이전트가 그대로 붙여넣는다(차트 1·2·3·4 = project_pie·category_pie·daily_trend_table·completion_table). 표 시각화 규칙(한 칸 환산, ▓/░ 10칸)은 기존 프롬프트 7-3·7-4와 동일하며, **표 하단 캡션 라인(한 칸 환산 단위·평균·누락 일자, 완료율 정렬 기준)까지 블록에 포함**해 에이전트가 수치를 만들 일이 없게 한다.

### 4.6 weekly 프롬프트 통합

- **Phase 2 서두에 "5-0. 결정적 집계 실행" 추가**:
  1. MCP로 읽은 일일보고 원문을 스크래치 임시 디렉토리에 `YYYY-MM-DD.md`로 저장
  2. 스크립트 경로 해석: `~/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py` → (없으면) 리포 체크아웃 내 `agents/workflow/weekly-work-reporter/scripts/aggregate_weekly.py` → (둘 다 없으면) 인라인 휴리스틱 폴백
  3. `python`(실패 시 `python3`)으로 실행, `--prev-weekly`는 전주 보고서 확보 시 지정
  4. JSON 파싱 성공 시: 7-1~7-4 수치·차트 4종은 **스크립트 출력을 정본으로 사용**(재계산 금지). `charts.*` 블록 그대로 삽입
  5. 스크립트 실패(파이썬 부재·비정상 종료·JSON 파싱 실패) 시: 기존 인라인 휴리스틱(7-1~7-4)으로 폴백하고, 보고서 캡션에 산정 방식(스크립트/휴리스틱)을 명시
- 기존 7-1~7-4 섹션은 "폴백 산정 규칙"으로 유지(삭제 금지 — 스크립트와 동일 규칙의 이중 정의임을 주석으로 명시).
- Constraints에 추가: "스크립트 집계가 성공한 경우 차트 수치를 임의 수정하지 말 것".

---

## 5. A-3 — 날짜 축 연속성

### 5.1 daily: 전일 보고서 참조 (Phase 2에 단계 추가)

- **전일 탐색**: 오늘 이전 날짜로 최대 5일 역순 탐색(`일일업무보고/YYYY-MM-DD.md` 존재 확인, 주말 무관 — 존재하는 가장 최근 보고서). 없으면 이 단계 전체를 조용히 생략.
- **이월 제안**: 전일 보고서의 "내일 할 일" 항목 중 오늘 사용자 입력·git 로그와 중복되지 않는 것을 사용자에게 제시 — "어제 계획하신 다음 항목들을 오늘 보고서에 반영할까요?" 사용자가 승인한 항목만, 지정한 섹션(기본: 진행 중인 일, 진행률은 사용자 확인)으로 포함. **미승인 항목은 절대 추가하지 않는다**(임의 추가 금지 원칙 유지 — Obsidian recent-changes와 동일 패턴).
- **진행률 연속성**: 오늘 항목이 전일 "진행 중인 일" 항목과 동일(기술 용어/제목 기준)하면:
  - 사용자가 진행률을 말하지 않은 경우 → 질문에 맥락 제공: "어제 60%였던 [제목], 오늘은 몇 %인가요?"
  - 사용자가 말한 진행률이 전일보다 **낮으면** → 후퇴가 맞는지 1회 확인(오기 방지). 사용자가 맞다고 하면 그대로 기록(재질문 금지).
- Constraints의 "업무 내용 임의 추가 금지" 문구를 "사용자 입력 + git 로그 + **전일 보고서 이월(사용자 승인 항목만)** 기반"으로 갱신.

### 5.2 weekly: 전주 보고서 참조 (Phase 1에 단계 추가)

- **전주 파일 탐색**: 두 가지 파일명 규약을 모두 시도 — ① 에이전트 규약 `주간업무보고/YYYY-WNN.md`(전주 ISO 주차), ② zero-touch 캐스케이드 규약 `주간업무보고/{전주월요일}~{전주금요일}.md`. 둘 다 없으면 조용히 생략(기존 동작).
- **활용**:
  - 확보 시 `--prev-weekly`로 스크립트에 전달 → 이월(carryover) 실측 판정 + `stats.prev_week` WoW 수치.
  - "주간 통계"에 라인 추가: `- 전주 대비: 완료 N건 (+M / -M)` (prev_week가 null이면 라인 생략 — 추정 금지).
  - Executive Summary: WoW 변화가 두드러질 때(완료 건수 ±30% 이상 등 서술 판단) 1개 불릿에 반영 가능(선택).
  - "신규 착수" 통계: carryover가 실측된 경우 `carryover=false`인 항목 수로 대체(더 정확). null이면 기존 방식(해당 주 최초 등장) 유지하되 캡션에 "주 내 기준" 명시.

---

## 6. A-4 — 마감(status) 연동 + 커맨드 수렴

### 6.1 daily: confirmed 보고서 보호

- Phase 2(기존 보고서 감지)에서 frontmatter `status` 파싱.
- `status: confirmed`이면 병합 진행 전 경고: "이 보고서는 이미 마감(confirmed)되었습니다. 수정을 진행할까요?" — 명시적 승인 시에만 진행. 저장 후 "수정이 반영되었으니 `/일일마감`으로 재확정을 권장합니다" 안내.
- `status` 필드 자체는 **변경하지 않는다**(마감 스킬 소관).

### 6.2 weekly: 확정 현황 반영

- 일일보고 frontmatter `status`를 스크립트가 수집(4.5 `days[].status`, `stats.confirmed_reports`).
- "주간 통계"에 라인 추가: `- 확정(마감) 보고서: N건 / M건`. 미확정(draft/없음) 일자가 있으면 캡션에 해당 날짜 나열.

### 6.3 커맨드 수렴: 리포 `commands/` (신규 디렉토리)

- `commands/일일마감.md`, `commands/주간마감.md` — 현재 `~/.claude/commands/`의 내용을 그대로 리포에 수록(정본 승격).
- `commands/README.md` — 각 커맨드 용도 1줄 + 배포 방법(`sync-agents.ps1`) 안내.
- 이후 커맨드 수정은 리포에서 하고 sync로 배포(에이전트와 동일 수명주기).
- 주의: `주간마감.md`는 zero-touch 절대 경로를 참조하는 머신 종속 커맨드 — 원문 그대로 수록하되 README에 머신 종속성 명시.

---

## 7. 버전·문서 갱신

| 파일 | 변경 |
|---|---|
| `daily-work-reporter.md` | 5.1 + 6.1 반영 (Phase 2 단계 추가, Constraints·Starting Instructions 갱신) |
| `daily-work-reporter/agent.json` | version `1.2.0 → 1.3.0`, capabilities에 전일 이월 제안·진행률 연속성·confirmed 보호 추가 |
| `daily-work-reporter/README.md` | 신기능 사용법 문단 추가 |
| `weekly-work-reporter.md` | 4.6 + 5.2 + 6.2 반영 (Phase 1·2 단계 추가, 차트 정본 규칙, Constraints·Starting Instructions 갱신) |
| `weekly-work-reporter/agent.json` | version `1.3.0 → 1.4.0`, capabilities에 결정적 집계·WoW·이월 실측·확정 카운트 추가 |
| `weekly-work-reporter/README.md` | 스크립트 요구사항(Python 3.9+)·폴백 동작 문단 추가 |
| 루트 `README.md` | sync 스크립트 안내 1문단 |

## 8. 후위호환 원칙 (전 항목 공통)

1. 전일/전주 보고서 부재 → 해당 단계 조용히 생략(기존 동작과 동일).
2. Python/스크립트 부재 → 인라인 휴리스틱 폴백(기존 동작과 동일). 보고서 캡션에 산정 방식 명시.
3. `status` frontmatter 부재 → 경고·카운트 없이 기존 동작.
4. 구형식 일일보고(태그 없음) → 스크립트도 프롬프트와 동일한 폴백 추론(프로젝트 H2·frontmatter·"일반 업무").
5. 배포 동기화는 리포 무대응 배포 파일을 건드리지 않음.

## 9. 테스트 전략

- **A-2 (필수, pytest)**: fixtures로 일일보고 5종 — ① 신형식 풀 메타데이터 ② 구형식(태그·진행률만) ③ 하루 2프로젝트 혼재 ④ 시간 명시·미명시 혼합 ⑤ confirmed/draft frontmatter 혼재 + 전주 주간보고 fixture 1종. 검증: 파이 합계=100(양쪽), 최대 그룹 잔차 흡수, 진행률 델타(다일 병합), 이월 실측, 누락 평일 목록, 카테고리 휴리스틱 폴백, unparsed 보존, 처리 건수 정의(내일 할 일 제외).
- **A-1 (수동 검증)**: 리포트 모드 표 출력·종료 코드, `-Apply` 후 해시 일치, 리포 무대응 파일 불변, `-Agent` 필터, 스크립트 배포(`agent-scripts`) 확인.
- **A-3/A-4 (프롬프트 회귀)**: 각 에이전트 .md의 신규 단계가 기존 절대 규칙(임의 추가 금지·원본 무수정 등)과 모순되지 않는지 정독 리뷰. 전일/전주/status 부재 시나리오의 "조용히 생략" 경로 명시 확인.

## 10. 구현 순서·의존성

1. **T1**: `scripts/sync-agents.ps1` + `commands/` 디렉토리 + 루트 README 갱신 (독립)
2. **T2**: `aggregate_weekly.py` + fixtures + pytest (독립 — 인터페이스는 본 spec 4.2·4.5가 정본)
3. **T3**: daily 프롬프트·agent.json·README 갱신 (독립)
4. **T4**: weekly 프롬프트·agent.json·README 갱신 (T2의 인터페이스 참조 — spec 기준으로 병행 가능)
5. **T5**: 테스트 실행 → `sync-agents.ps1 -Apply`로 실제 드리프트 해소 → 배포본 해시 검증 (T1~T4 완료 후)

## 11. 명시적 비범위 (YAGNI)

- 프로젝트 레지스트리·멤버십 규칙(`_config/work-agents.yaml`) — 별도 spec의 Phase 1
- `--draft-only` 모드, n8n/스케줄러, 웹 뷰어 — 별도 spec의 Phase 2
- 과거 보고서 일괄 마이그레이션·재작성 — 하지 않음
- 의미 기반(fuzzy) 동일 업무 병합의 스크립트화 — LLM 서술 보정으로 유지
