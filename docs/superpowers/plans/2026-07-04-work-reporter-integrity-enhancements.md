# 일일·주간 업무보고 에이전트 정합성 고도화 (A안) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** daily/weekly 업무보고 에이전트의 배포 동기화(A-1), 주간 집계 결정화(A-2), 날짜 축 연속성(A-3), 마감 연동(A-4)을 구현한다.

**Architecture:** 리포(정본) → `~/.claude` 배포본을 동기화하는 비대화형 PowerShell 스크립트, weekly 집계를 결정적으로 수행하는 stdlib-only Python 스크립트(+pytest 골든 테스트), 두 에이전트 프롬프트(.md)의 단계 추가. Spec: `docs/superpowers/specs/2026-07-04-work-reporter-integrity-enhancements-design.md` (인터페이스 정본).

**Tech Stack:** PowerShell 7 (pwsh), Python 3.9+ (표준 라이브러리만), pytest, 마크다운 시스템 프롬프트

## Global Constraints

- Python은 3.9+ 문법만 사용 (`Optional[str]`, `str | None` 금지), **외부 패키지 금지** (frontmatter는 정규식 파싱)
- Windows 콘솔 인코딩 대응: Python 스크립트 main()에서 `sys.stdout.reconfigure(encoding="utf-8")`, 모든 파일 IO `encoding="utf-8"`
- JSON 출력은 `ensure_ascii=False`
- PowerShell 스크립트는 완전 비대화형 (`Read-Host` 금지), `#!/usr/bin/env pwsh` 셔뱅
- 배포본은 리포 파일과 **바이트 동일 사본** (스탬프·변형 금지), 리포에 대응 파일이 없는 배포 파일은 절대 건드리지 않음
- 커밋 메시지: conventional commits (`feat:`, `test:`, `docs:`), **Co-Authored-By·Claude 생성 마커 절대 금지** (사용자 글로벌 규칙)
- 에이전트 프롬프트(.md) 수정은 기존 문체·구조(한국어, Phase/번호 체계) 유지, 기존 규칙 삭제 금지(폴백으로 강등만 허용)
- 모든 신규 동작은 후위호환: 전일/전주/스크립트/status 부재 시 기존 동작과 동일 (조용히 생략)

---

### Task 1: 배포 동기화 스크립트 + 커맨드 수렴 (A-1, A-4 일부)

**Files:**
- Create: `scripts/sync-agents.ps1`
- Create: `commands/일일마감.md` (원본: `C:\Users\ATL\.claude\commands\일일마감.md` 그대로 복사)
- Create: `commands/주간마감.md` (원본: `C:\Users\ATL\.claude\commands\주간마감.md` 그대로 복사)
- Create: `commands/README.md`
- Modify: 루트 `README.md` (설치 안내 부근에 동기화 문단 추가)

**Interfaces:**
- Consumes: `agents/{category}/{name}/agent.json`(version 필드), `agents/{category}/{name}/{name}.md`, `agents/*/*/scripts/*`(test_*·fixtures 제외), `commands/*.md`(README 제외)
- Produces: CLI `pwsh scripts/sync-agents.ps1 [-Apply] [-All] [-Agent <names>] [-Dest <path>]`. 종료 코드: 리포트 모드 0=드리프트 없음/1=있음, Apply 모드 0=성공/1=실패 항목 존재. 배포 경로: `<Dest>\agents\<name>.md`, `<Dest>\agent-scripts\<name>\<file>`, `<Dest>\commands\<file>.md` (Dest 기본 `$HOME\.claude`)

- [ ] **Step 1: 커맨드 파일 수렴**

`~/.claude/commands/일일마감.md`와 `~/.claude/commands/주간마감.md`를 **내용 그대로** `commands/`에 복사한다 (바이트 동일해야 sync 리포트가 IDENTICAL로 나온다):

```powershell
New-Item -ItemType Directory -Force commands | Out-Null
Copy-Item "$HOME\.claude\commands\일일마감.md" commands\
Copy-Item "$HOME\.claude\commands\주간마감.md" commands\
```

`commands/README.md` 작성:

```markdown
# Commands

Claude Code 슬래시 커맨드 정본. 수정은 이 디렉토리에서 하고 `scripts/sync-agents.ps1 -Apply`로 `~/.claude/commands/`에 배포한다.

| 커맨드 | 용도 |
|---|---|
| `일일마감` | 당일(또는 지정 날짜) 일일업무보고를 검토·확정(`status: confirmed`) |
| `주간마감` | 주간 마감 캐스케이드(주간보고 → 팀장브리핑 → PPT)를 대화형 실행 |

> 주의: `주간마감.md`는 zero-touch 리포의 절대 경로(`C:\Users\ATL\...`)를 참조하는 머신 종속 커맨드다.
```

- [ ] **Step 2: sync-agents.ps1 작성**

```powershell
#!/usr/bin/env pwsh
<#
sync-agents.ps1 — 리포(정본) → ~/.claude 배포본 동기화 (비대화형)

사용법 (리포 루트에서 실행):
  pwsh scripts/sync-agents.ps1                 # 드리프트 리포트만 (무변경)
  pwsh scripts/sync-agents.ps1 -Apply          # DIFFERENT 항목만 갱신
  pwsh scripts/sync-agents.ps1 -Apply -All     # NOT_DEPLOYED 항목도 설치
  pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter -Apply
  pwsh scripts/sync-agents.ps1 -Dest <path>    # 기본: $HOME\.claude

종료 코드: 리포트 모드 0=전부 IDENTICAL, 1=드리프트 존재 / Apply 모드 0=성공, 1=실패 항목 존재
-Agent 필터는 에이전트(및 번들 스크립트)에만 적용되며 commands/*.md는 항상 포함된다.
#>
param(
    [switch]$Apply,
    [switch]$All,
    [string[]]$Agent,
    [string]$Dest = (Join-Path $HOME ".claude")
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path "agents")) {
    Write-Host "오류: 리포 루트에서 실행하세요 ('agents' 디렉토리 없음)"
    exit 1
}

function Get-Sha256([string]$Path) { (Get-FileHash -Path $Path -Algorithm SHA256).Hash }

$items = @()

# 1) 에이전트 .md + 번들 스크립트 (test_*, fixtures 제외)
foreach ($categoryDir in Get-ChildItem -Path "agents" -Directory) {
    foreach ($agentDir in Get-ChildItem -Path $categoryDir.FullName -Directory) {
        $name = $agentDir.Name
        $json = Join-Path $agentDir.FullName "agent.json"
        $md   = Join-Path $agentDir.FullName "$name.md"
        if (-not (Test-Path $json) -or -not (Test-Path $md)) { continue }
        if ($Agent -and $name -notin $Agent) { continue }
        $version = (Get-Content $json -Raw | ConvertFrom-Json).version
        $items += [pscustomobject]@{ Kind='agent'; Name=$name; Source=$md
            Target=(Join-Path $Dest "agents\$name.md"); Version=$version }
        $scriptsDir = Join-Path $agentDir.FullName "scripts"
        if (Test-Path $scriptsDir) {
            foreach ($f in Get-ChildItem $scriptsDir -File) {
                if ($f.Name -like 'test_*') { continue }
                $items += [pscustomobject]@{ Kind='script'; Name="$name/$($f.Name)"; Source=$f.FullName
                    Target=(Join-Path $Dest "agent-scripts\$name\$($f.Name)"); Version=$version }
            }
        }
    }
}

# 2) 커맨드 (필터 무관 항상 포함)
if (Test-Path "commands") {
    foreach ($f in Get-ChildItem "commands" -Filter *.md -File) {
        if ($f.Name -eq 'README.md') { continue }
        $items += [pscustomobject]@{ Kind='command'; Name=$f.BaseName; Source=$f.FullName
            Target=(Join-Path $Dest "commands\$($f.Name)"); Version='' }
    }
}

$report = foreach ($i in $items) {
    $status = if (-not (Test-Path $i.Target)) { 'NOT_DEPLOYED' }
              elseif ((Get-Sha256 $i.Source) -eq (Get-Sha256 $i.Target)) { 'IDENTICAL' }
              else { 'DIFFERENT' }
    [pscustomobject]@{ Kind=$i.Kind; Name=$i.Name; Version=$i.Version; Status=$status
                       Source=$i.Source; Target=$i.Target }
}

$report | Format-Table Kind, Name, Version, Status -AutoSize | Out-String | Write-Host

if ($Apply) {
    $failed = 0
    $targets = @($report | Where-Object { $_.Status -eq 'DIFFERENT' -or ($All -and $_.Status -eq 'NOT_DEPLOYED') })
    foreach ($t in $targets) {
        try {
            $dir = Split-Path $t.Target -Parent
            if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
            Copy-Item -Path $t.Source -Destination $t.Target -Force
            Write-Host "[SYNCED] $($t.Kind) $($t.Name)"
        } catch {
            Write-Host "[FAIL] $($t.Kind) $($t.Name): $_"
            $failed++
        }
    }
    if ($targets.Count -eq 0) { Write-Host "변경 없음 — 모두 동기화 상태입니다." }
    exit ([int]($failed -gt 0))
} else {
    $drift = @($report | Where-Object { $_.Status -ne 'IDENTICAL' }).Count
    Write-Host ("드리프트: {0}건 / 전체 {1}건" -f $drift, $report.Count)
    exit ([int]($drift -gt 0))
}
```

- [ ] **Step 3: 리포트 모드 수동 검증**

Run: `pwsh scripts/sync-agents.ps1` (리포 루트에서)
Expected: 표에 `daily-work-reporter`·`weekly-work-reporter`가 `DIFFERENT`, `일일마감`·`주간마감` 커맨드가 `IDENTICAL`, 종료 코드 1(`$LASTEXITCODE`). 배포 디렉토리 파일은 변경되지 않음.

Run: `pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter`
Expected: 에이전트는 daily 1건만 표시되고 커맨드 2건은 여전히 표시됨.

- [ ] **Step 4: 루트 README에 동기화 안내 추가**

루트 `README.md`의 설치(Installation/설치) 관련 섹션 뒤에 추가:

```markdown
### 배포 동기화 (sync-agents.ps1)

리포는 정본이고 실제 실행은 `~/.claude/agents/`의 배포본을 사용한다. 두 위치의 드리프트를 감지·해소하려면:

```powershell
pwsh scripts/sync-agents.ps1          # 드리프트 리포트 (무변경, 종료코드 1=드리프트 존재)
pwsh scripts/sync-agents.ps1 -Apply   # 이미 배포된 항목 갱신 (-All: 신규 설치 포함)
```

에이전트 번들 스크립트는 `~/.claude/agent-scripts/<agent>/`로, `commands/*.md`는 `~/.claude/commands/`로 함께 배포된다. 리포에 대응 파일이 없는 배포 파일은 건드리지 않는다.
```

- [ ] **Step 5: Commit**

```bash
git add scripts/sync-agents.ps1 commands/ README.md
git commit -m "feat: add non-interactive deploy sync script and converge close commands into repo"
```

---

### Task 2: 결정적 집계 스크립트 aggregate_weekly.py (A-2 + A-3/A-4 데이터)

**Files:**
- Create: `agents/workflow/weekly-work-reporter/scripts/aggregate_weekly.py`
- Create: `agents/workflow/weekly-work-reporter/scripts/test_aggregate_weekly.py`
- Create: `agents/workflow/weekly-work-reporter/scripts/fixtures/daily/2026-06-22.md` (외 4개 일일 fixture, 전주 주간 fixture 1개)

**Interfaces:**
- Consumes: 없음 (독립 스크립트, spec §4가 정본)
- Produces:
  - `aggregate(daily_dir, week_start=None, week_end=None, prev_weekly=None, include_weekends=False) -> dict` — spec §4.5 JSON 스키마의 dict 반환 (모든 인자 str/bool)
  - `fold_small_groups(scores) -> dict` — 5% 미만 그룹 "기타" 통합 (2개 이상 소그룹일 때만)
  - CLI: `python aggregate_weekly.py --dir D [--week-start YYYY-MM-DD] [--week-end YYYY-MM-DD] [--prev-weekly F] [--include-weekends] [--out F]` → JSON stdout(또는 --out)
  - Task 4의 weekly 프롬프트가 이 CLI와 JSON 키(`merged/projects/categories/days/stats/charts/meta/tomorrow_plans/unparsed`)를 참조

- [ ] **Step 1: fixtures 작성**

`fixtures/daily/2026-06-22.md`:

```markdown
---
date: 2026-06-22
type: 일일업무보고
tags: [daily-report, work-log]
status: confirmed
---

# 일일업무보고 - 2026년 06월 22일

## 오늘 한 일
- **[BUG] 로그인 오류 수정** `100/100%` `{web_frontend}` `(2h)` `[P0]`
  - 로그인 시 화면 멈춤 현상 원인 파악 및 수정
  - 원인: 서버 응답 대기 시간 초과
  - (PR #456, JIRA: AXIS-1234)
  - (session timeout 버그 수정)

## 진행 중인 일
- **[FEAT] 결제 기능 개발** `30/100%` `{payment_service}` `(0.5d)`
  - 핵심 결제 로직 설계
  - (결제 모듈 개발)

## 내일 할 일
- **[QA] 결제 테스트 작성** `0/100%` `{payment_service}`
  - 결제 로직 자동 검사 도구 제작 예정
  - (결제 모듈 테스트 코드)

## 특이사항
- **팀 회의** `[Minor]`
  - 주간 일정 공유
```

`fixtures/daily/2026-06-23.md` (구형식 + 프로젝트 H2 + 파싱 불가 라인):

```markdown
---
date: 2026-06-23
type: 일일업무보고
tags: [daily-report, work-log]
---

# 일일업무보고 - 2026년 06월 23일

## 진행 중인 일
- **결제 기능 개발** `50/100%`
  - 결제 로직 구현 계속
  - (결제 모듈 개발)
- 참고: 결제 일정 회의는 목요일로 연기

## ATL-RAMS
- **국제화 리소스 정리** `100/100%`
  - 다국어 텍스트 파일 구조 정리
  - 미사용 리소스 제거
  - (i18n 리소스 정리)
```

`fixtures/daily/2026-06-25.md`:

```markdown
---
date: 2026-06-25
type: 일일업무보고
tags: [daily-report, work-log]
status: confirmed
---

# 일일업무보고 - 2026년 06월 25일

## 오늘 한 일
- **[DOC] 주간보고 에이전트 개선** `100/100%` `{custom_subagents}` `(4h)`
  - 주간보고 자동 생성 도구 기능 보강
  - (weekly-work-reporter 프롬프트 개선)

## 진행 중인 일
- **[FEAT] 결제 기능 개발** `80/100%` `{payment_service}`
  - 화면 연동 마무리 단계
  - (결제 모듈 개발)

## 내일 할 일
- **[OPS] 배포 준비** `0/100%` `{payment_service}`
  - 운영 반영 사전 점검 예정
  - (배포 파이프라인 점검)
```

`fixtures/daily/2026-06-26.md`:

```markdown
---
date: 2026-06-26
type: 일일업무보고
tags: [daily-report, work-log]
status: draft
---

# 일일업무보고 - 2026년 06월 26일

## 진행 중인 일
- **[FEAT] 결제 기능 개발** `90/100%` `{payment_service}`
  - 예외 처리 로직 추가
  - (결제 모듈 개발)
- **[QA] 결제 테스트 작성** `40/100%` `{payment_service}`
  - 핵심 흐름 검사 도구 절반 작성
  - (결제 모듈 테스트 코드)
```

`fixtures/daily/2026-06-27.md` (토요일 — 기본 제외 검증용):

```markdown
---
date: 2026-06-27
type: 일일업무보고
tags: [daily-report, work-log]
---

# 일일업무보고 - 2026년 06월 27일

## 오늘 한 일
- **주말 문서 정리** `100/100%`
  - 개인 노트 정리
  - (문서 정리)
```

`fixtures/prev_weekly.md`:

```markdown
---
date: 2026-06-19
type: 주간업무보고
week: 2026-W25
period: 2026-06-15 ~ 2026-06-19
tags: [weekly-report, work-log]
---

# 주간업무보고 - 2026년 6월 3주차 (06/15 ~ 06/19)

## Executive Summary
- 결제 모듈 개발 착수

## 프로젝트별 주간 실적

### payment_service

#### 진행 중
- **결제 기능 개발** `10/100% → 30/100%`
  - 요구사항 분석 및 설계
  - (결제 모듈 개발)

## 다음 주 계획
- **결제 기능 개발** `30/100%`
  - 핵심 로직 구현
  - (결제 모듈 개발)

## 주간 통계
- 분석 기간: 2026-06-15(월) ~ 2026-06-19(금)
- 일일보고서: 5건 / 5건
- 완료 업무: 5건
- 진행 중 업무: 1건
- 신규 착수: 3건
- 다음 주 이월: 1건
```

- [ ] **Step 2: 실패하는 테스트 작성** (`test_aggregate_weekly.py` — 전체 코드, 기대값의 산출 근거는 이 태스크 끝 "기대값 도출표" 참조)

```python
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import aggregate_weekly as agg

FIX = Path(__file__).parent / "fixtures"
DAILY = FIX / "daily"
PREV = FIX / "prev_weekly.md"

WEEK = dict(week_start="2026-06-22", week_end="2026-06-26")


def run(**kw):
    return agg.aggregate(str(DAILY), **{**WEEK, **kw})


def merged_by_term(result, term):
    return next(m for m in result["merged"] if m["tech_term"] == term)


# ---- meta / days ----

def test_meta_dates_and_missing_weekdays():
    r = run()
    assert r["meta"]["analyzed_dates"] == ["2026-06-22", "2026-06-23", "2026-06-25", "2026-06-26"]
    assert r["meta"]["missing_weekdays"] == ["2026-06-24"]
    iso = date(2026, 6, 22).isocalendar()
    assert r["meta"]["iso_week"] == f"{iso[0]}-W{iso[1]:02d}"


def test_weekend_excluded_by_default():
    # 토요일(06-27)은 범위를 넓혀도 기본 제외, include_weekends=True일 때만 포함
    r = agg.aggregate(str(DAILY), week_start="2026-06-22", week_end="2026-06-28")
    assert "2026-06-27" not in r["meta"]["analyzed_dates"]
    r2 = agg.aggregate(str(DAILY), week_start="2026-06-22", week_end="2026-06-28",
                       include_weekends=True)
    assert "2026-06-27" in r2["meta"]["analyzed_dates"]


def test_confirmed_and_draft_status():
    r = run()
    assert r["meta"]["confirmed_dates"] == ["2026-06-22", "2026-06-25"]
    assert r["meta"]["draft_dates"] == ["2026-06-26"]
    assert r["stats"]["confirmed_reports"] == 2
    assert r["stats"]["total_reports"] == 4


def test_daily_counts_exclude_tomorrow_and_notes():
    r = run()
    days = {d["date"]: d for d in r["days"]}
    assert days["2026-06-22"]["item_count"] == 2      # 오늘 한 일 1 + 진행 중 1 (내일/특이사항 제외)
    assert days["2026-06-22"]["completed_count"] == 1
    assert days["2026-06-23"]["item_count"] == 2      # 진행 중 1 + 프로젝트 H2 1
    assert days["2026-06-26"]["completed_count"] == 0
    assert days["2026-06-22"]["status"] == "confirmed"
    assert days["2026-06-23"]["status"] == "none"
    assert days["2026-06-26"]["status"] == "draft"


def test_unparsed_preserved():
    r = run()
    assert r["meta"]["unparsed_count"] == 1
    assert any("목요일로 연기" in u["text"] for u in r["unparsed"])


# ---- merging / progress ----

def test_multi_day_merge_and_progress_delta():
    r = run()
    m = merged_by_term(r, "결제 모듈 개발")
    assert m["days_seen"] == 4
    assert m["start_pct"] == 30 and m["end_pct"] == 90
    assert m["completed"] is False


def test_merged_project_uses_latest_explicit_tag():
    r = run()
    # 화요일(태그 없음)이 프로젝트를 "일반 업무"로 덮어쓰지 않아야 한다
    assert merged_by_term(r, "결제 모듈 개발")["project"] == "payment_service"


def test_project_from_h2_header():
    r = run()
    assert merged_by_term(r, "i18n 리소스 정리")["project"] == "ATL-RAMS"


def test_metadata_extraction():
    r = run()
    m = merged_by_term(r, "session timeout 버그 수정")
    assert m["category"] == "BUG"
    assert m["hours_total"] == 2.0
    assert m["priority"] == "P0"
    assert any("PR #456" in i for i in m["identifiers"])


# ---- effort / normalization ----

def test_project_effort_percentages_sum_100():
    r = run()
    pcts = {p["name"]: p["effort_pct"] for p in r["projects"]}
    assert sum(pcts.values()) == 100
    assert pcts == {"payment_service": 40, "custom_subagents": 29, "ATL-RAMS": 17, "web_frontend": 14}


def test_category_percentages_sum_100():
    r = run()
    pcts = {c["tag"]: c["pct"] for c in r["categories"]}
    assert sum(pcts.values()) == 100
    assert pcts["FEAT"] == 29 and pcts["BUG"] == 14 and pcts["QA"] == 11


def test_category_heuristic_fallback():
    r = run()
    # 명시 태그 없음 + 제목 "정리" 키워드 → REFACTOR
    assert merged_by_term(r, "i18n 리소스 정리")["category"] == "REFACTOR"


def test_completion_rates():
    r = run()
    p = {x["name"]: x for x in r["projects"]}
    assert p["payment_service"]["done_count"] == 0 and p["payment_service"]["wip_count"] == 2
    assert p["web_frontend"]["completion_pct"] == 100
    assert p["payment_service"]["completion_pct"] == 0


def test_small_groups_folded_into_etc():
    assert agg.fold_small_groups({"a": 50.0, "b": 44.0, "c": 3.0, "d": 3.0}) == {"a": 50.0, "b": 44.0, "기타": 6.0}
    # 소그룹이 1개뿐이면 유지
    assert agg.fold_small_groups({"a": 97.0, "b": 3.0}) == {"a": 97.0, "b": 3.0}


# ---- carryover / WoW ----

def test_carryover_null_without_prev_weekly():
    r = run()
    assert all(m["carryover"] is None for m in r["merged"])
    assert r["stats"]["carried_in"] is None


def test_carryover_and_wow_with_prev_weekly():
    r = run(prev_weekly=str(PREV))
    assert merged_by_term(r, "결제 모듈 개발")["carryover"] is True
    assert merged_by_term(r, "session timeout 버그 수정")["carryover"] is False
    assert r["stats"]["carried_in"] == 1
    assert r["stats"]["new_started"] == 4
    assert r["stats"]["prev_week"]["done"] == 5
    assert r["stats"]["prev_week"]["wow_done_delta"] == -2   # 이번 주 완료 3 - 전주 5


# ---- stats / plans ----

def test_stats_done_wip_carry_next():
    r = run()
    assert r["stats"]["done"] == 3
    assert r["stats"]["wip"] == 2
    assert r["stats"]["carry_next"] == 2


def test_tomorrow_plans_collected():
    r = run()
    titles = [t["title"] for t in r["tomorrow_plans"]]
    assert "결제 테스트 작성" in titles and "배포 준비" in titles


# ---- charts ----

def test_chart_blocks_ready_to_paste():
    r = run()
    pie = r["charts"]["project_pie"]
    assert pie.startswith("```mermaid\npie showData title")
    assert '"payment_service" : 40' in pie
    assert pie.rstrip().endswith("```")
    table = r["charts"]["daily_trend_table"]
    assert "| 06-22 | 월 | 2건 |" in table
    assert "▓▓░░░░░░░░" in table          # 한 칸=1건 스케일에서 2건
    assert "100%" in r["charts"]["completion_table"]


def test_cli_outputs_valid_json():
    out = subprocess.run(
        [sys.executable, str(Path(agg.__file__)), "--dir", str(DAILY),
         "--week-start", "2026-06-22", "--week-end", "2026-06-26"],
        capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0
    assert json.loads(out.stdout)["stats"]["done"] == 3
```

**기대값 도출표 (구현·디버깅 시 참조):**

| 병합 항목 (tech_term 기준) | 프로젝트 | 카테고리 | 진행률 | 공수 점수 | 산출 근거 |
|---|---|---|---|---|---|
| session timeout 버그 수정 | web_frontend | BUG | 100 (단일일) | **2.0** | 시간 명시 2h |
| 결제 모듈 개발 | payment_service | FEAT | 30→90, 4일 | **4.0** | 시간 명시 0.5d=4h (시간 있으면 시간 우선) |
| i18n 리소스 정리 | ATL-RAMS (H2) | REFACTOR (휴리스틱) | 100 단일일 | **2.4** | 1.0 + 델타 1.0(단일일=end/100) + 복잡도 0.4(설명 불릿 2×0.2) |
| weekly-work-reporter 프롬프트 개선 | custom_subagents | DOC | 100 단일일 | **4.0** | 시간 명시 4h |
| 결제 모듈 테스트 코드 | payment_service | QA | 40 단일일 | **1.6** | 1.0 + 델타 0.4 + 복잡도 0.2(설명 불릿 1) |

- 프로젝트 합산: payment 5.6 / custom 4.0 / RAMS 2.4 / web 2.0, 총 14.0 → 40/29(28.57)/17(17.14)/14(14.29)%, 합 100 (잔차 0)
- 카테고리 합산(공수 점수 기준): FEAT 4.0→29 / DOC 4.0→29 / REFACTOR 2.4→17 / BUG 2.0→14 / QA 1.6→11
- 복잡도 카운트에서 **식별자 라인과 괄호 원문(기술 용어) 라인은 제외**한 설명 불릿만 센다
- 일자별 처리 건수 = "오늘 한 일" + "진행 중인 일" + 프로젝트 H2 항목 (내일 할 일·특이사항·unparsed 제외)

- [ ] **Step 3: 테스트 실패 확인**

Run: `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v` (리포 루트에서)
Expected: `ModuleNotFoundError: No module named 'aggregate_weekly'` 또는 전체 FAIL

- [ ] **Step 4: aggregate_weekly.py 구현**

spec §4.2~4.5가 인터페이스 정본. 아래는 모듈 골격과 오차가 생기기 쉬운 핵심 알고리즘의 확정 코드 — 이 코드와 시그니처를 그대로 사용하고, 파일 순회·파싱 조립·JSON 구성은 테스트를 통과하도록 구현한다:

```python
#!/usr/bin/env python3
"""주간업무보고 결정적 집계 (stdlib only, Python 3.9+).

일일업무보고 .md 디렉토리를 파싱해 병합·공수·카테고리·차트 데이터를 JSON으로 출력한다.
weekly-work-reporter 프롬프트 7-1~7-4와 동일 규칙의 결정적 구현.
"""
import argparse
import json
import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path

CATEGORY_SECTIONS = ("오늘 한 일", "진행 중인 일", "내일 할 일", "특이사항")
WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
EFFORT_KEYWORDS = ("풀스택", "Phase", "마이그레이션", "신규 구현", "재설계", "근본 수정")
CATEGORY_KEYWORDS = {  # 선언 순서 = 판정 우선순위 (weekly 프롬프트 7-2와 동일)
    "FEAT": ("신규", "구현", "도입", "Phase", "신설", "추가", "출시"),
    "BUG": ("수정", "오류", "에러", "버그", "fix", "핫픽스", "근본 수정"),
    "REFACTOR": ("리팩터", "정합", "정리", "복원", "안정화", "재설계"),
    "OPS": ("배포", "마이그레이션", "인프라", "환경", "스크립트", "CI/CD"),
    "DOC": ("문서", "README", "보고서", "에이전트", "가이드"),
    "QA": ("테스트", "검증", "QA", "회귀"),
}
LABELS_KR = {"FEAT": "신규 개발", "BUG": "버그 수정", "REFACTOR": "리팩토링",
             "OPS": "운영·배포", "DOC": "문서·자동화", "QA": "테스트"}

ITEM_RE = re.compile(r"^- \*\*(?:\[(FEAT|BUG|REFACTOR|OPS|DOC|QA)\]\s*)?(.+?)\*\*(.*)$")
TOKEN_PROGRESS = re.compile(r"`(\d{1,3})/100%`")
TOKEN_PROJECT = re.compile(r"`\{([^}]+)\}`")
TOKEN_HOURS = re.compile(r"`\((\d+(?:\.\d+)?)(h|d)\)`")
TOKEN_PRIORITY = re.compile(r"`\[(P0|P1|P2|Critical|Major|Minor)\]`")
IDENTIFIER_RE = re.compile(r"^\((?:PR |JIRA:|이슈 ).*\)$")


def normalize_key(text):
    """병합 키 정규화: 소문자화 + 공백/구두점 제거."""
    return re.sub(r"[\s\.\,\:\;\-\_\(\)\[\]\{\}·]+", "", text.lower())


def fold_small_groups(scores):
    """5% 미만 그룹을 '기타'로 통합. 소그룹이 2개 이상일 때만 (1개면 유지)."""
    total = sum(scores.values())
    if total <= 0:
        return dict(scores)
    small = [k for k, v in scores.items() if v / total * 100 < 5]
    if len(small) < 2:
        return dict(scores)
    out = {k: v for k, v in scores.items() if k not in small}
    out["기타"] = sum(scores[k] for k in small)
    return out


def normalize_pcts(scores):
    """점수 dict → 합계 정확히 100인 정수 % dict (최대 점수 그룹이 잔차 흡수)."""
    total = sum(scores.values())
    if total <= 0:
        return {k: 0 for k in scores}
    pcts = {k: round(v / total * 100) for k, v in scores.items()}
    diff = 100 - sum(pcts.values())
    if pcts and diff:
        largest = max(pcts, key=lambda k: scores[k])
        pcts[largest] += diff
    return pcts


def effort_score(item_merged):
    """병합 항목 1건의 공수 점수. 시간 명시 항목은 시간 합(1d=8h), 아니면 휴리스틱."""
    if item_merged["hours_total"] is not None:
        return item_merged["hours_total"]
    score = 1.0
    if item_merged["days_seen"] == 1:
        score += (item_merged["end_pct"] or 0) / 100          # 단일 등장: 시작값 0 간주
    else:
        score += ((item_merged["end_pct"] or 0) - (item_merged["start_pct"] or 0)) / 100
    score += min(item_merged["max_desc_bullets"] * 0.2, 1.0)  # 복잡도(설명 불릿, 식별자·원문 제외)
    kw = sum(0.5 for k in EFFORT_KEYWORDS
             if k in item_merged["title"] or k in (item_merged["tech_term"] or ""))
    score += min(kw, 1.5)
    score += min(0.3 * (item_merged["days_seen"] - 1), 1.5)
    return score


def pct_bar(pct):
    """완료율(0~100) → ▓/░ 10칸 바."""
    filled = round(pct / 10)
    return "▓" * filled + "░" * (10 - filled)


def count_bar(count, unit):
    """처리 건수 → ▓/░ 10칸 바. unit = ceil(최대 건수 / 10)."""
    filled = min(10, round(count / unit))
    return "▓" * filled + "░" * (10 - filled)


def mermaid_pie(title, pcts):
    """합계 100 정수 % dict → 펜스 포함 Mermaid pie 블록 (0% 항목 생략)."""
    lines = ["```mermaid", f"pie showData title {title}"]
    for name, pct in sorted(pcts.items(), key=lambda kv: -kv[1]):
        if pct > 0:
            lines.append(f'    "{name}" : {pct}')
    lines.append("```")
    return "\n".join(lines)


def aggregate(daily_dir, week_start=None, week_end=None, prev_weekly=None,
              include_weekends=False):
    """spec §4.5 스키마의 dict 반환. 구현 요구사항:
    - daily_dir의 YYYY-MM-DD.md 전수 → 날짜 범위·주말 필터
    - frontmatter(date/status/total_hours/focus_project) 정규식 파싱
    - H2 분리: CATEGORY_SECTIONS는 카테고리 섹션, 그 외 H2는 프로젝트 헤더
    - 항목: ITEM_RE 매칭 실패한 최상위 불릿은 unparsed로 보존
    - 항목 프로젝트: 인라인 태그 > 프로젝트 H2 > frontmatter project > '일반 업무'
    - 병합 키: normalize_key(tech_term or title); 병합 프로젝트는
      '명시 인라인 태그가 있는 가장 늦은 날짜'의 태그 (없으면 폴백 판정값)
    - 처리 건수: '오늘 한 일'+'진행 중인 일'+프로젝트 H2 항목 (내일/특이사항/unparsed 제외)
    - carryover: prev_weekly 지정 시 그 파일의 '진행 중'(H4)·'다음 주 계획' 항목 키 대조,
      미지정 시 None; stats.prev_week는 '주간 통계'의 '완료 업무: N건' 파싱 (실패 시 None)
    - charts 4종: mermaid_pie / 표+캡션 문자열 완성본 (테스트의 형식 단언 참조)
    """
    ...


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--week-start")
    parser.add_argument("--week-end")
    parser.add_argument("--prev-weekly")
    parser.add_argument("--include-weekends", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()
    result = aggregate(args.dir, args.week_start, args.week_end,
                       args.prev_weekly, args.include_weekends)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
```

차트 문자열 형식 (테스트가 단언하는 정확한 형식):
- `daily_trend_table` 행: `| 06-22 | 월 | 2건 | ▓▓░░░░░░░░ |`, 헤더 `| 날짜 | 요일 | 처리 건수 | 시각화 |`, 하단 캡션 `> 한 칸 = N건 환산. 누락 일자: [...]. 평균 약 N.N건/일.`
- `completion_table` 행: `| 프로젝트명 | N | N | ▓▓▓▓▓▓▓▓▓▓ 100% |`, 완료율 내림차순, 하단 캡션 포함
- pie title: `프로젝트별 공수 배분 (YYYY-WNN)` / `업무 유형별 비중 (YYYY-WNN)`, 카테고리 pie 라벨은 `신규 개발 [FEAT]` 형식(`LABELS_KR[tag] + " [" + tag + "]"`)

- [ ] **Step 5: 테스트 통과 확인**

Run: `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v`
Expected: 전체 PASS (20개 테스트)

- [ ] **Step 6: Commit**

```bash
git add agents/workflow/weekly-work-reporter/scripts/
git commit -m "feat: add deterministic weekly aggregation script with golden fixture tests"
```

---

### Task 3: daily-work-reporter 프롬프트 갱신 (A-3 연속성 + A-4 confirmed 보호)

**Files:**
- Modify: `agents/workflow/daily-work-reporter/daily-work-reporter.md`
- Modify: `agents/workflow/daily-work-reporter/agent.json`
- Modify: `agents/workflow/daily-work-reporter/README.md`

**Interfaces:**
- Consumes: `일일업무보고/YYYY-MM-DD.md` 파일 규약, frontmatter `status: confirmed`(일일마감 커맨드가 부여)
- Produces: 프롬프트 신규 단계 Phase 1.5(3-1~3-3)·5-1 — Task 5의 배포 대상

- [ ] **Step 1: Phase 1.5 삽입**

`daily-work-reporter.md`에서 `### Phase 2: 기존 보고서 감지` 라인 **바로 앞**에 삽입:

```markdown
### Phase 1.5: 전일 보고서 참조 (연속성)

3-1. **전일 보고서 탐색**
   - 오늘 이전 날짜로 최대 5일까지 역순으로 `일일업무보고/YYYY-MM-DD.md` 존재 확인 (`mcp__obsidian__obsidian_get_file_contents`, 가장 최근 1건만 사용)
   - 어떤 파일도 없으면 이 Phase 전체를 조용히 생략 (기존 동작과 동일)

3-2. **이월 후보 제안 (사용자 승인 필수)**
   - 전일 보고서의 "내일 할 일" 항목 중, 오늘 사용자 입력·git 로그와 의미상 중복되지 않는 항목을 추출
   - 사용자에게 목록 제시: "어제 계획하신 다음 항목들을 오늘 보고서에 반영할까요?"
   - **승인된 항목만** 포함 — 기본 배치는 "진행 중인 일"(진행률은 사용자에게 확인), 완료했다고 답하면 "오늘 한 일"
   - 미승인 항목은 절대 추가하지 않음 (임의 추가 금지 원칙 유지)

3-3. **진행률 연속성 확인**
   - 오늘 항목이 전일 "진행 중인 일" 항목과 동일(괄호 원문 기술 용어 또는 제목 기준)하면 전일 진행률을 기준점으로 사용
   - 사용자가 진행률을 언급하지 않은 경우: "어제 N%였던 [제목], 오늘은 몇 %인가요?" 형식으로 질문
   - 사용자가 말한 진행률이 전일보다 낮으면 1회만 확인 질문 (오기 방지). 사용자가 맞다고 하면 그대로 기록하고 재질문 금지
```

- [ ] **Step 2: confirmed 보호 단계 삽입**

`6. **저장 모드 결정**` 라인 **바로 앞**에 삽입:

```markdown
5-1. **마감(confirmed) 보호 확인**
   - 감지된 기존 보고서의 frontmatter `status` 값 확인
   - `status: confirmed`이면 병합 진행 전 경고: "이 보고서는 이미 마감(confirmed)되었습니다. 수정을 진행할까요?"
   - 사용자가 명시적으로 승인한 경우에만 병합 진행, 거부 시 중단
   - `status` 필드 자체는 변경하지 않음 (마감·재확정은 `/일일마감` 커맨드 소관)
   - 저장 완료 안내에 "수정이 반영되었으니 `/일일마감`으로 재확정을 권장합니다" 포함
```

- [ ] **Step 3: Constraints·Starting Instructions 갱신**

기존 라인 교체 ①:

```
- 업무 내용 임의 추가 금지 (사용자 입력 + git 로그 기반만)
```
→
```
- 업무 내용 임의 추가 금지 (사용자 입력 + git 로그 + 전일 보고서 이월 중 **사용자 승인 항목**만)
```

Constraints "절대 규칙"에 1줄 추가 (기존 CRITICAL 목록 마지막에):

```
- **CRITICAL**: `status: confirmed` 보고서는 사용자의 명시적 승인 없이 수정하지 않을 것
```

`## Starting Instructions`의 번호 목록 전체를 다음으로 교체:

```markdown
1. 사용자 입력에서 업무 내용 파악 + 카테고리 태그 키워드 추론
2. git 로그 자동 확인 (Bash) + 커밋 prefix 카테고리 매핑 + PR/이슈 식별자 자동 추출 + 프로젝트 폴더명 캡처(`git rev-parse --show-toplevel` basename, 실패 시 작업 디렉토리 basename, 둘 다 불가 시 생략)
3. 전일 보고서 확인 (최대 5일 역순, 없으면 생략) → 이월 후보 사용자 승인 + 진행률 연속성 반영
4. Obsidian에서 오늘 날짜 기존 보고서 확인 — `status: confirmed`면 수정 진행 여부 확인
5. 사용자가 시간·우선순위·합계를 명시한 경우 메타데이터 부착 (미명시 시 생략)
6. 기술 용어 변환 + 보고서 초안 작성 (메타데이터 표기 규칙 준수)
7. 초안을 사용자에게 보여주기
8. 사용자 확인 후 Obsidian에 저장
9. 저장 결과 안내 (confirmed 보고서 수정이었으면 `/일일마감` 재확정 권장)
```

- [ ] **Step 4: agent.json 갱신**

`"version": "1.2.0"` → `"version": "1.3.0"`, `capabilities` 배열 끝에 추가:

```json
"전일 보고서의 '내일 할 일' 기반 이월 후보 제안 (사용자 승인 항목만 반영)",
"전일 진행률 기준 연속성 확인 (미언급 시 맥락 질문, 진행률 후퇴 시 1회 확인)",
"마감(status: confirmed) 보고서 수정 시 경고 및 /일일마감 재확정 안내"
```

- [ ] **Step 5: README.md 기능 문단 추가**

daily README의 기능(Features) 섹션에 추가:

```markdown
### 연속성 및 마감 연동 (v1.3.0)

- **전일 이월 제안**: 어제(최대 5일 역순) 보고서의 "내일 할 일"을 오늘 초안에 반영할지 물어봅니다. 승인한 항목만 포함됩니다.
- **진행률 연속성**: 어제 "진행 중"이던 업무는 어제 진행률을 기준으로 질문하며, 진행률이 후퇴하면 한 번 확인합니다.
- **마감 보호**: `/일일마감`으로 확정(`status: confirmed`)된 보고서는 명시적 승인 없이 수정하지 않으며, 수정 후 재확정을 안내합니다.
```

- [ ] **Step 6: 정합성 검토 후 Commit**

프롬프트 전체를 다시 읽어 새 단계가 기존 CRITICAL 규칙과 모순되지 않는지 확인 (특히 "기존 보고서 내용을 삭제하지 않을 것" / "임의 추가 금지" / 번호 체계 충돌 없음).

```bash
git add agents/workflow/daily-work-reporter/
git commit -m "feat: add previous-day continuity and confirmed-report protection to daily-work-reporter"
```

---

### Task 4: weekly-work-reporter 프롬프트 갱신 (A-2 통합 + A-3 전주 + A-4 확정 카운트)

**Files:**
- Modify: `agents/workflow/weekly-work-reporter/weekly-work-reporter.md`
- Modify: `agents/workflow/weekly-work-reporter/agent.json`
- Modify: `agents/workflow/weekly-work-reporter/README.md`

**Interfaces:**
- Consumes: Task 2의 CLI(`aggregate_weekly.py --dir ... --week-start ... --week-end ... [--prev-weekly ...]`)와 JSON 키(`merged/projects/categories/days/stats/charts/meta/tomorrow_plans`), 배포 경로 `~/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py`
- Produces: 프롬프트 신규 단계 4-1(전주 확인)·5-0(결정적 집계) — Task 5의 배포 대상

- [ ] **Step 1: Phase 1에 전주 확인 단계 삽입**

`### Phase 2: 데이터 분석 및 집계` 라인 **바로 앞**(4. 기존 주간보고서 확인 단계 뒤)에 삽입:

```markdown
4-1. **전주 주간보고서 확인 (연속성, 선택적)**
   - 전주 ISO 주차를 계산하고 두 파일명 규약을 순서대로 시도:
     * `주간업무보고/YYYY-WNN.md` (에이전트 규약, 전주 주차)
     * `주간업무보고/{전주 월요일}~{전주 금요일}.md` (zero-touch 캐스케이드 규약)
   - 발견 시 내용을 확보하여 5-0의 결정적 집계에 `--prev-weekly`로 전달
   - 둘 다 없으면 조용히 생략 — 이월 판정은 "주 내 최초 등장" 기준 폴백, "전주 대비" 라인 생략 (추정 금지)
```

- [ ] **Step 2: Phase 2 서두에 5-0 결정적 집계 단계 삽입**

`5. **일일보고서 파싱**` 라인 **바로 앞**에 삽입:

```markdown
5-0. **결정적 집계 실행 (스크립트 우선)**
   - MCP로 읽은 일일보고 원문을 임시 디렉토리(스크래치)에 `YYYY-MM-DD.md` 파일로 저장 (전주 주간보고 확보 시 함께 저장)
   - 스크립트 경로 해석 (순서대로 최초 존재 경로 사용):
     1. `~/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py` (sync 배포본)
     2. 리포 체크아웃 내 `agents/workflow/weekly-work-reporter/scripts/aggregate_weekly.py`
   - 실행: `python aggregate_weekly.py --dir <임시디렉토리> --week-start <월요일> --week-end <금요일> [--prev-weekly <전주보고서 임시파일>]` (`python` 실패 시 `python3` 재시도)
   - **성공 시** (유효한 JSON 반환): 이후 5~7-4단계의 수치·병합·차트는 스크립트 출력을 정본으로 사용
     * `merged`/`projects`/`categories`/`days`/`stats` → 각 섹션·통계의 수치
     * `charts` 4종 블록(project_pie/category_pie/daily_trend_table/completion_table)은 **그대로 삽입** (재계산·수정 금지)
     * 의미상 유사하나 철자가 다른 항목의 추가 병합은 서술에서만 보정하고 수치는 스크립트 값 유지
     * 보고서의 공수 캡션에 "스크립트 집계" 명시
   - **실패 시** (python 부재·비정상 종료·JSON 파싱 실패): 아래 5~7-4의 인라인 휴리스틱으로 폴백, 캡션에 "휴리스틱 집계" 명시
```

그리고 `7-1. **프로젝트별 공수(Effort) 점수 산정** (필수)` 라인 **바로 앞**에 안내 인용문 추가:

```markdown
> 7-1~7-4는 5-0 스크립트 집계 **실패 시의 폴백** 산정 규칙이다. 스크립트(`aggregate_weekly.py`)는 아래와 동일한 규칙의 결정적 구현이며, 규칙 수정 시 양쪽을 함께 갱신해야 한다.
```

- [ ] **Step 3: 주간 통계 형식 + 신규 착수 정의 갱신**

주간보고서 형식 템플릿의 `## 주간 통계` 블록을 다음으로 교체:

```markdown
## 주간 통계
- 분석 기간: YYYY-MM-DD(월) ~ YYYY-MM-DD(금)
- 일일보고서: N건 / 5건
- 확정(마감) 보고서: N건 / M건
- 완료 업무: N건
- 전주 대비: 완료 N건 (ΔM건)
- 진행 중 업무: N건
- 신규 착수: N건
- 다음 주 이월: N건
```

교체 직후에 인용문 추가:

```markdown
> "확정(마감) 보고서"는 frontmatter `status: confirmed` 기준. 미확정 일자가 있으면 캡션에 날짜 나열. "전주 대비" 라인은 전주 주간보고를 확보한 경우에만 표기 (미확보 시 라인 생략 — 추정 금지).
```

`7. **주간 집계 산출**`의 `- 신규 착수 업무 (해당 주에 처음 등장한 업무)` 라인을 교체:

```
- 신규 착수 업무: 전주 보고서 확보 시 carryover=false 항목 수(실측), 미확보 시 해당 주 최초 등장 기준(캡션에 "주 내 기준" 명시)
```

- [ ] **Step 4: Constraints·Starting Instructions 갱신**

Constraints "절대 규칙"에 추가:

```
- **CRITICAL**: 5-0 스크립트 집계가 성공한 경우 차트·통계 수치를 임의로 수정하지 말 것 (`charts` 블록은 원문 그대로 삽입)
```

`## Starting Instructions`의 번호 목록 전체를 다음으로 교체:

```markdown
1. 사용자 입력에서 대상 주차 파악 (미지정시 이번 주 자동 계산)
2. Bash로 Python 원라이너 실행하여 월~금 날짜 목록 및 ISO 주차 계산
3. Obsidian에서 `일일업무보고/` 디렉토리 파일 목록 조회
4. 대상 주의 평일(월~금) 파일만 필터링하여 읽기
5. 전주 주간보고서 확인 (`YYYY-WNN.md` → `{월}~{금}.md` 순서 시도, 없으면 생략)
6. **결정적 집계 실행 (5-0)**: 일일보고 원문을 임시 디렉토리에 저장 → `aggregate_weekly.py` 실행 (배포 경로 → 리포 경로 순, 전주 보고서 확보 시 `--prev-weekly` 전달)
   - 성공: 병합·공수·유형·일자별·완료 현황·이월·전주 대비 수치와 차트 4종 = 스크립트 출력 정본
   - 실패: 7-1~7-4 인라인 휴리스틱 폴백 (캡션에 산정 방식 명시)
7. 프로젝트별 그룹핑·중복 병합·진행률 추적 검토 (스크립트 성공 시 결과 검증·서술만, 실패 시 직접 수행)
8. 차트 4종 배치 (스크립트 성공 시 `charts` 블록 그대로, 실패 시 직접 생성 — 절대 생략 금지)
9. Executive Summary + 차트 4종 + 프로젝트별 상세 + 특이사항 + 리스크 + 다음 주 계획 + 통계(확정 보고서 수·전주 대비 포함) 작성
10. (선택) 차트화 보강 제안이 의미 있는 경우 사용자에게 메타데이터 보강 제안
11. 초안을 사용자에게 보여주기
12. 사용자 확인 후 Obsidian `주간업무보고/YYYY-WNN.md`에 저장
    - patch 사용 시 **H1::H2 헤딩 경로** 필수 (단순 H2 텍스트는 invalid-target)
13. 저장 결과 안내
```

- [ ] **Step 5: agent.json 갱신**

`"version": "1.3.0"` → `"version": "1.4.0"`, `capabilities` 배열 끝에 추가:

```json
"번들 스크립트(aggregate_weekly.py) 기반 결정적 집계 — 병합·공수·차트 수치의 재현성 보장 (실패 시 인라인 휴리스틱 자동 폴백)",
"전주 주간보고서 자동 탐색 (YYYY-WNN·날짜범위 이중 파일명 규약) 기반 이월 실측 판정",
"전주 대비(WoW) 완료 건수 비교 라인 생성 (전주 보고서 확보 시에만)",
"일일보고 frontmatter status 기반 확정(마감) 보고서 카운트 표기"
```

- [ ] **Step 6: README.md 요구사항 문단 추가**

weekly README에 추가:

```markdown
### 결정적 집계 스크립트 (v1.4.0)

주간 수치(병합·공수·유형·일자별·완료 현황)와 차트 4종은 번들 스크립트 `scripts/aggregate_weekly.py`(Python 3.9+, 표준 라이브러리만 사용)가 결정적으로 산출합니다. `scripts/sync-agents.ps1 -Apply` 실행 시 `~/.claude/agent-scripts/weekly-work-reporter/`로 함께 배포됩니다. Python이 없거나 스크립트 실행에 실패하면 기존 인라인 휴리스틱으로 자동 폴백하며, 보고서 캡션에 산정 방식이 표기됩니다.

추가로 전주 주간보고서를 자동 탐색하여 이월 여부를 실측하고 "전주 대비" 통계 라인을 생성하며, 일일보고의 `status: confirmed`(마감) 여부를 주간 통계에 집계합니다.
```

- [ ] **Step 7: 정합성 검토 후 Commit**

프롬프트 전체를 다시 읽어 확인: 5-0↔7-x 폴백 관계 명확, "차트 4종 절대 생략 금지" CRITICAL과 모순 없음, 주간 통계 형식과 Starting Instructions 일치.

```bash
git add agents/workflow/weekly-work-reporter/
git commit -m "feat: integrate deterministic aggregation, prev-week continuity, and confirmed counts into weekly-work-reporter"
```

---

### Task 5: 전체 검증 + 배포 동기화 실행 (A-1 실적용)

**Files:**
- Modify: `~/.claude/agents/daily-work-reporter.md`, `~/.claude/agents/weekly-work-reporter.md`, `~/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py` (sync -Apply 결과물, 리포 파일 아님)

**Interfaces:**
- Consumes: Task 1의 `sync-agents.ps1`, Task 2~4의 완성 산출물

- [ ] **Step 1: 전체 테스트 재실행**

Run: `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v`
Expected: 전체 PASS

- [ ] **Step 2: 드리프트 리포트 확인**

Run: `pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter`
Expected: daily/weekly 에이전트 `DIFFERENT`, `weekly-work-reporter/aggregate_weekly.py` 스크립트 `NOT_DEPLOYED`, 커맨드 2건 `IDENTICAL`, 종료 코드 1

- [ ] **Step 3: 적용 (범위: daily/weekly만 — 다른 에이전트 배포본은 이번 범위 밖)**

Run: `pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter -Apply -All`
Expected: `[SYNCED] agent daily-work-reporter`, `[SYNCED] agent weekly-work-reporter`, `[SYNCED] script weekly-work-reporter/aggregate_weekly.py`, 종료 코드 0

- [ ] **Step 4: 배포 검증**

Run: `pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter`
Expected: 해당 항목 전부 `IDENTICAL`, 종료 코드 0

Run: `python "$HOME/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py" --dir agents/workflow/weekly-work-reporter/scripts/fixtures/daily --week-start 2026-06-22 --week-end 2026-06-26`
Expected: 유효한 JSON 출력 (배포본 스모크 테스트)

- [ ] **Step 5: 최종 Commit (잔여 변경이 있을 경우)**

```bash
git status --short
git add docs/superpowers/
git commit -m "docs: add integrity enhancement spec and implementation plan for work reporters"
```
