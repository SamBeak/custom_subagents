# 설정 코어 Phase 1 (프로젝트 레지스트리) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 폴더명에 묶인 암묵적 프로젝트 개념을 vault `_config/work-agents.yaml` 정본(레지스트리+멤버십+가감 규칙)으로 바꾸고, 4개 업무 에이전트(daily/weekly/pm-board/wbs-gantt)가 이를 단일 소스로 참조하게 한다.

**Architecture:** 설계 정본은 `docs/superpowers/specs/2026-06-15-work-agents-config-monitoring-platform-design.md` §3~4. 알고리즘 정본은 신규 `agents/_shared/config-contract.md`(드리프트 방지용 SSOT). 4개 프롬프트에 공통 "Phase 0" 블록을 lockstep 삽입. weekly의 결정적 집계 스크립트(`aggregate_weekly.py`)는 `--config`(canonical JSON)를 받아 레지스트리 정규화·가감을 수치 레벨에서 적용. config 부재 시 4개 에이전트 전부 기존 동작 무변경(3중 폴백).

**Tech Stack:** 마크다운 시스템 프롬프트, Python 3.9+ stdlib(스크립트), pytest, Obsidian MCP(YAML 정본 읽기)

## Global Constraints

- config 정본은 **vault `_config/work-agents.yaml`** — 리포에는 동일 내용의 `agents/_shared/work-agents.sample.yaml`을 수록(배포 시 vault로 복사되는 원본)
- **후위호환 3중 폴백** (스펙 §4.6 그대로): ① config 없음 → 기존 폴더-basename 동작 ② 해석 실패 → `{미배정}`(조용히 버리지 않고, 추정도 안 함) ③ 옛 보고서의 옛 태그 → alias 흡수
- **config 부재 시 스크립트 출력 완전 동일**: 기존 pytest 21건은 단 한 글자도 수정 없이 통과해야 함 (신규 meta 키 추가는 허용 — 기존 테스트는 키 부재를 단언하지 않음)
- 표시는 registry `name`, 내부 그룹 키는 `id` (스펙 §4.4: 인라인 태그는 `{name}`)
- Python 3.9+ 문법만(`typing.Optional`, `str | None` 금지), stdlib only, 파일 IO `encoding="utf-8"`, `ensure_ascii=False`
- 스크립트는 YAML을 직접 파싱하지 않는다 — **weekly 에이전트(LLM)가 YAML을 canonical JSON으로 직렬화**해 임시 디렉토리에 저장 후 `--config`로 전달 (계약 §5)
- 에이전트 프롬프트 수정: 기존 문체·구조 유지, 기존 규칙 삭제 금지, 기존 스텝 번호 재부여 금지(신규는 0-x 하위 번호), **4개 lockstep**
- 각 에이전트 README에 기능 문단 + **Version History 행** 둘 다 추가 (A안 리뷰 교훈)
- 버전: daily `1.3.0→1.4.0`, weekly `1.4.0→1.5.0`, pm-board `1.0.0→1.1.0`, wbs-gantt `1.0.0→1.1.0`
- 커밋: conventional commits, **Co-Authored-By·Claude 생성 마커 절대 금지**

---

### Task 1: config 계약 문서 + 샘플 config

**Files:**
- Create: `agents/_shared/config-contract.md`
- Create: `agents/_shared/work-agents.sample.yaml`

**Interfaces:**
- Produces: 계약 문서의 resolve 알고리즘·스키마·가감 적용표 — Task 2~6 전부가 이 계약을 정본으로 참조. 샘플 YAML은 Task 7에서 vault `_config/work-agents.yaml`로 복사되는 원본.

- [ ] **Step 1: `agents/_shared/work-agents.sample.yaml` 작성** (사용자 승인 드래프트 — 그대로 사용)

```yaml
# work-agents.yaml — 업무 에이전트 단일 정본 설정
# 정본 위치: Obsidian vault `_config/work-agents.yaml` (이 파일은 리포 샘플/원본)
# 스키마·해석 규칙: agents/_shared/config-contract.md
version: 1

paths:
  daily_dir: 일일업무보고
  weekly_dir: 주간업무보고
  pm_board: PM보드/PM-Board.md
  wbs_dir: 프로젝트관리

# ── ① 프로젝트 레지스트리 (id=불변 내부 키, name=표시명, aliases=철자변형 흡수) ──
projects:
  - id: atl-axis
    name: ATL AXIS
    aliases: [atl_axis, AXIS]
    status: active
  - id: atl-home
    name: ATL 홈페이지
    aliases: [atl_home]
    status: active
  - id: atl-rams
    name: ATL-RAMS
    aliases: [atl-rams, ramsa, RAMS, ATL-RAMS ALE]
    status: active
  - id: lean-buff
    name: Lean Buff
    aliases: [lean_buff]
    status: active
  - id: printage
    name: Printage
    aliases: [printage]
    status: active
  - id: pm-automation
    name: 사내 PM 자동화
    aliases: [custom_subagents, zero-touch]
    status: active

# ── ② 멤버십 규칙 (위→아래 우선순위 매칭; 실패 → 미배정) ──
membership:
  - { match: { jira_prefix: "AXIS-" }, project: atl-axis }
  - { match: { folder: atl_axis }, project: atl-axis }
  - { match: { folder: atl_home }, project: atl-home }
  - { match: { folder: atl-rams }, project: atl-rams }
  - { match: { folder: ramsa }, project: atl-rams }
  - { match: { folder: lean_buff }, project: lean-buff }
  - { match: { folder: printage }, project: printage }
  - { match: { folder: custom_subagents }, project: pm-automation }
  - { match: { folder: zero-touch }, project: pm-automation }

# ── ③ 수집 가감 규칙 ──
rules:
  global:
    exclude_commit_prefixes: [chore, build, ci]
    git: { since: midnight, max_count: 50 }
  per_project: {}
  thresholds: { stall_days: 3, wip_limit: 8, promise_window: 3 }

vocab:
  glossary_extra: []
  commit_prefix_map: {}
```

- [ ] **Step 2: `agents/_shared/config-contract.md` 작성**

```markdown
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
| `paths.daily_dir/weekly_dir/pm_board/wbs_dir` | 프롬프트 하드코딩 경로의 오버라이드 (없는 키는 기존 기본값) | 4개 전부 |
| `projects[]: {id, name, aliases[], status, deadline?, milestones?}` | 프로젝트 레지스트리. id=불변 내부 키(그룹핑), name=표시명(태그·차트·보드 노출), aliases=모든 철자변형 | 4개 전부 |
| `membership[]: {match: {folder?|path_glob?|jira_prefix?}, project: <id>}` | 폴더/경로/식별자 → 프로젝트 매칭 규칙, **위→아래 첫 매칭 승리** | daily(태깅 시), wbs(소속 선별) |
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
```

- [ ] **Step 3: Commit**

```bash
git add agents/_shared/
git commit -m "feat: add config contract and sample registry for work agents"
```

---

### Task 2: aggregate_weekly.py `--config` 확장

**Files:**
- Modify: `agents/workflow/weekly-work-reporter/scripts/aggregate_weekly.py`
- Modify: `agents/workflow/weekly-work-reporter/scripts/test_aggregate_weekly.py` (테스트 추가만 — 기존 21건 무수정)
- Create: `agents/workflow/weekly-work-reporter/scripts/fixtures/config.json`

**Interfaces:**
- Consumes: Task 1 계약 §3(정규화 규칙 = 기존 `normalize_key`), §5(JSON 스키마·소비 키)
- Produces:
  - CLI: 기존 플래그 + `--config <json파일>` (선택)
  - `aggregate(..., config=None)` — 새 keyword 인자 `config`(str 경로 또는 None)
  - `load_config(path) -> Optional[dict]` — 파일 없음/JSON 오류/`projects` 배열 부재 시 None
  - `resolve_project(raw, registry_index) -> tuple` — `(표시명, 프로젝트 id 또는 None, registered_bool)`; index None이면 `(raw, None, True)`
  - JSON 출력 추가 키: `meta.config_loaded`(bool), `meta.unregistered_projects`(list), `meta.excluded_count`(int)
  - Task 4의 weekly 프롬프트가 이 플래그·키를 참조

- [ ] **Step 1: config fixture 작성** — `fixtures/config.json`

```json
{
  "version": 1,
  "projects": [
    { "id": "payment", "name": "결제 서비스", "aliases": ["payment_service"], "status": "active" },
    { "id": "atl-rams", "name": "ATL-RAMS", "aliases": ["ramsa", "RAMS"], "status": "active" },
    { "id": "pm-automation", "name": "사내 PM 자동화", "aliases": ["custom_subagents", "zero-touch"], "status": "active" }
  ],
  "membership": [],
  "rules": {
    "per_project": { "pm-automation": { "exclude_keywords": ["실험"] } },
    "thresholds": { "stall_days": 3, "wip_limit": 8, "promise_window": 3 }
  }
}
```

(주의: `web_frontend`는 의도적으로 미등록 — unregistered 경로 검증용)

- [ ] **Step 2: 실패하는 테스트 추가** — `test_aggregate_weekly.py` 끝에 append (기존 테스트 무수정)

```python
# ---- config (B안: 프로젝트 레지스트리) ----

CONFIG = FIX / "config.json"


def write_daily(tmp_path, date_str, body):
    (tmp_path / f"{date_str}.md").write_text(
        f"---\ndate: {date_str}\ntype: 일일업무보고\n---\n\n# 일일업무보고\n\n{body}",
        encoding="utf-8")


def test_config_normalizes_aliases_to_registry_names():
    r = run(config=str(CONFIG))
    names = {p["name"] for p in r["projects"]}
    assert "결제 서비스" in names and "payment_service" not in names
    assert "사내 PM 자동화" in names and "custom_subagents" not in names
    assert "ATL-RAMS" in names                      # name 일치는 그대로
    assert r["meta"]["config_loaded"] is True


def test_config_preserves_effort_pcts_after_rename():
    r = run(config=str(CONFIG))
    pcts = {p["name"]: p["effort_pct"] for p in r["projects"]}
    assert pcts == {"결제 서비스": 40, "사내 PM 자동화": 29, "ATL-RAMS": 17, "web_frontend": 14}


def test_config_unregistered_kept_and_reported():
    r = run(config=str(CONFIG))
    assert r["meta"]["unregistered_projects"] == ["web_frontend"]
    assert any(p["name"] == "web_frontend" for p in r["projects"])   # 미배정으로 뭉개지 않음


def test_config_chart_labels_use_registry_names():
    r = run(config=str(CONFIG))
    assert '"결제 서비스" : 40' in r["charts"]["project_pie"]


def test_config_absent_behavior_unchanged():
    r = run()
    assert r["meta"]["config_loaded"] is False
    assert any(p["name"] == "payment_service" for p in r["projects"])
    assert r["meta"]["unregistered_projects"] == []


def test_config_invalid_json_ignored(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text("{not json", encoding="utf-8")
    r = run(config=str(bad))
    assert r["meta"]["config_loaded"] is False
    assert any(p["name"] == "payment_service" for p in r["projects"])


def test_config_exclude_keywords_filters_items(tmp_path):
    write_daily(tmp_path, "2026-06-29", (
        "## 오늘 한 일\n"
        "- **[DOC] 프롬프트 실험 기록** `100/100%` `{custom_subagents}`\n"
        "  - 임시 실험 노트 정리\n"
        "  - (프롬프트 실험)\n"
        "- **[DOC] 에이전트 가이드 갱신** `100/100%` `{custom_subagents}`\n"
        "  - 사용 가이드 문서 갱신\n"
        "  - (agent guide 갱신)\n"))
    r = agg.aggregate(str(tmp_path), week_start="2026-06-29", week_end="2026-07-03",
                      config=str(CONFIG))
    terms = [m["tech_term"] for m in r["merged"]]
    assert "agent guide 갱신" in terms and "프롬프트 실험" not in terms
    assert r["meta"]["excluded_count"] == 1


def test_config_alias_merges_split_tags(tmp_path):
    write_daily(tmp_path, "2026-06-29", (
        "## 진행 중인 일\n"
        "- **다국어 지원 개선** `30/100%` `{RAMS}`\n"
        "  - 리소스 구조 정리\n"
        "  - (i18n 개선)\n"))
    write_daily(tmp_path, "2026-06-30", (
        "## 진행 중인 일\n"
        "- **다국어 지원 개선** `60/100%` `{ramsa}`\n"
        "  - 번역 키 정리\n"
        "  - (i18n 개선)\n"))
    r = agg.aggregate(str(tmp_path), week_start="2026-06-29", week_end="2026-07-03",
                      config=str(CONFIG))
    assert len(r["merged"]) == 1
    assert r["merged"][0]["project"] == "ATL-RAMS"       # 두 철자가 한 registry name으로
    assert [p["name"] for p in r["projects"]] == ["ATL-RAMS"]
```

그리고 파일 상단의 `run()` 헬퍼가 `config` kwarg를 통과시키는지 확인 — 기존 `run()`은
`agg.aggregate(str(DAILY), **{**WEEK, **kw})`이므로 kwarg가 그대로 전달된다 (수정 불필요).

- [ ] **Step 3: 테스트 실패 확인**

Run: `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v`
Expected: 기존 21건 PASS, 신규 8건 FAIL (`TypeError: aggregate() got an unexpected keyword argument 'config'` 등)

- [ ] **Step 4: 구현**

핵심 함수 (확정 코드 — 그대로 사용):

```python
def load_config(path):
    """--config JSON 로드. 파일 없음/JSON 오류/projects 배열 부재 → None (config 무시)."""
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(cfg, dict) or not isinstance(cfg.get("projects"), list):
        return None
    return cfg


def build_registry_index(config):
    """정규화 키 → 프로젝트 dict 매핑. id/name/aliases 전부 키로 등록."""
    index = {}
    for proj in config["projects"]:
        keys = [proj.get("id", ""), proj.get("name", "")] + list(proj.get("aliases", []))
        for k in keys:
            if k:
                index[normalize_key(str(k))] = proj
    return index


def resolve_project(raw, registry_index):
    """원시 프로젝트 문자열 → (표시명, 프로젝트 id, registered). 미등록은 원시값 유지."""
    if registry_index is None:
        return raw, None, True
    proj = registry_index.get(normalize_key(raw))
    if proj:
        return proj["name"], proj.get("id"), True
    return raw, None, False
```

`aggregate()` 통합 지점 (구현 요구사항):
1. 시그니처: `def aggregate(daily_dir, week_start=None, week_end=None, prev_weekly=None, include_weekends=False, config=None)`; `main()`에 `--config` argparse 추가 + 전달
2. `cfg = load_config(config)`; `registry = build_registry_index(cfg) if cfg else None`
3. **정규화 시점**: 병합(merged) 산출 직후, 공수·카테고리·완료율·차트 집계 **이전**에 각 merged 항목의
   `project`를 `resolve_project()`로 교체 — 이후 모든 집계·차트가 registry name 기준으로 동작
   (동일 name으로 정규화된 서로 다른 원시 태그는 같은 그룹으로 합산됨)
4. `"일반 업무"`는 resolve 대상에서 제외 (프로젝트 정보 없음 상태 유지)
5. **가감**: 정규화 후 `rules.per_project.<id>`를 조회 —
   registry name→id 역참조를 위해 resolve 시 `id`도 기억.
   `exclude_keywords` 중 하나가 제목 또는 기술용어에 포함되고 `always_include`에 걸리지 않으면
   해당 merged 항목 제거(`meta.excluded_count` 증가). 제외 항목은 stats/공수/카테고리/일자별
   카운트 전부에서 빠진다 — 일자별 카운트는 merged 제외 목록의 키와 대조해 감산
6. `meta.config_loaded` = cfg is not None; `meta.unregistered_projects` = registered=False였던
   원시명 정렬 목록(중복 제거); config 없으면 `[]`
7. carryover(`--prev-weekly`) 키 대조는 정규화와 무관 (기술용어/제목 기반 유지)

- [ ] **Step 5: 전체 테스트 통과 확인**

Run: `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v`
Expected: 29건 전체 PASS (기존 21 + 신규 8), 경고 없음

- [ ] **Step 6: Commit**

```bash
git add agents/workflow/weekly-work-reporter/scripts/
git commit -m "feat: add registry-based project normalization and rules to weekly aggregation"
```

---

### Task 3: daily-work-reporter Phase 0 (v1.4.0)

**Files:**
- Modify: `agents/workflow/daily-work-reporter/daily-work-reporter.md`
- Modify: `agents/workflow/daily-work-reporter/agent.json`
- Modify: `agents/workflow/daily-work-reporter/README.md`

**Interfaces:**
- Consumes: Task 1 계약 §3(resolve)·§4(daily 행)
- Produces: `{name}` / `{미배정}` 태그 규약 — Task 4~6의 소비자(weekly/pm/wbs)가 이 태그를 registry로 재해석

- [ ] **Step 1: Phase 0 블록 삽입** — `### Phase 1: 업무 내용 수집` 라인 **바로 앞**에 삽입:

```markdown
### Phase 0: 설정 로드 & 프로젝트 해석 (공통, 선택적)

0-1. **설정 정본 로드**
   - `mcp__obsidian__obsidian_get_file_contents`로 `_config/work-agents.yaml` 읽기 시도
   - 실패(404/연결 오류/YAML 파싱 불가) 시: **이 Phase 전체를 조용히 생략**하고 기존 동작 유지 (후위호환)

0-2. **설정 파싱**
   - `paths`/`projects`(레지스트리)/`membership`/`rules`/`vocab` 추출
   - `paths.daily_dir`가 있으면 일일업무보고 디렉토리 경로로 사용 (없으면 기존 `일일업무보고`)

0-3. **프로젝트 해석 규칙**
   - `resolve(원시값)`: 정규화(소문자·공백·구두점 무시) 후 ① `membership` 규칙 위→아래 매칭(folder/jira_prefix) ② 레지스트리 전역 id/name/aliases 일치 검색 → 매칭 프로젝트의 **표시명(name)** 사용
   - 매칭 실패 시 **`{미배정}`** — 임의 프로젝트명 생성 금지 (추정 금지 원칙 유지). 저장 완료 안내에서 "미배정 항목 N건 — `_config/work-agents.yaml`의 aliases에 폴더명을 추가하면 흡수됩니다" 안내
   - 상세 알고리즘 정본: `agents/_shared/config-contract.md` (수정 시 4개 에이전트 lockstep)
```

- [ ] **Step 2: Phase 1 git 수집·폴더 캡처 단계에 config 적용 추가** — `2. **git 로그 + 프로젝트 폴더명 보충 수집**` 단계의 마지막 불릿(`캡처한 폴더명은 이 보고서 항목들의 **기본 프로젝트 값**으로 사용`) **바로 뒤**에 같은 들여쓰기로 추가:

```markdown
   - **(Phase 0 성공 시) config 적용**:
     * git log 파라미터는 `rules.global.git`(since/max_count) 값 사용, `rules.global.exclude_commit_prefixes`에 해당하는 prefix 커밋은 수집에서 제외
     * `vocab.commit_prefix_map`이 있으면 커밋 prefix→카테고리 매핑을 그 값으로 오버라이드
     * 캡처한 폴더명을 `resolve()`로 해석 → 이후 태그는 `{폴더명}` 대신 **`{표시명(name)}`** 부착, 해석 실패 시 `{미배정}`
     * `vocab.glossary_extra`가 있으면 기술 용어 변환 사전에 추가 항목으로 사용
```

- [ ] **Step 3: 프로젝트 태그 표기 규칙 갱신** — `### 프로젝트 태그 표기 규칙` 섹션의 `**폴더명 소스 (Phase 1에서 캡처):**` 목록 **바로 뒤**에 추가:

```markdown
**config 연동 (Phase 0 성공 시):**
- 태그 값 = 캡처 폴더명을 레지스트리로 해석한 **표시명(name)** (예: 폴더 `custom_subagents` → `{사내 PM 자동화}`)
- 해석 실패 시 `{미배정}` 부착 — 옛 `{폴더명}` 태그와 혼재해도 소비자(weekly 등)가 alias로 흡수하므로 정상
- config 부재 시 기존 `{폴더명}` 그대로 (후위호환)
```

- [ ] **Step 4: Constraints·Starting Instructions 갱신**

금지 사항의 라인:
```
- **프로젝트명 추정 금지**: 폴더명 캡처(git/작업 디렉토리)가 불가하면 임의로 프로젝트명을 지어내지 말고 프로젝트 태그를 생략
```
을 다음으로 교체:
```
- **프로젝트명 추정 금지**: 폴더명 캡처(git/작업 디렉토리)가 불가하면 임의로 프로젝트명을 지어내지 말고 프로젝트 태그를 생략. config 레지스트리 해석 실패 시에도 지어내지 말고 `{미배정}` 부착
```

`## Starting Instructions` 목록에서 1번 항목 앞에 새 0번을 추가하고 기존 번호는 유지:
```markdown
0. `_config/work-agents.yaml` 로드 시도 (Phase 0) — 성공 시 레지스트리 해석·가감 활성, 실패 시 조용히 생략
```
그리고 기존 2번 항목 끝에 ` (config 성공 시: 가감 규칙 적용 + 폴더명 resolve → {표시명}/{미배정})`를 덧붙인다.

- [ ] **Step 5: agent.json + README**

`"version": "1.3.0"` → `"version": "1.4.0"`, capabilities 끝에 추가:
```json
"vault _config/work-agents.yaml 레지스트리 연동 — 폴더명을 프로젝트 표시명으로 해석해 {name} 태그 부착 (실패 시 {미배정}, config 부재 시 기존 동작)",
"config 수집 가감 적용 — 커밋 prefix 제외·git 파라미터·용어 사전 확장·커밋 카테고리 매핑 오버라이드"
```

README: 기능 섹션에 문단 추가 **그리고** Version History에 `### v1.4.0` 행 추가 (기존 스타일 미러링):
```markdown
### 프로젝트 레지스트리 연동 (v1.4.0)

vault `_config/work-agents.yaml`에 프로젝트 레지스트리를 정의하면, 폴더명 대신 프로젝트 **표시명**이 태그로 부착됩니다(예: `{custom_subagents}` → `{사내 PM 자동화}`). 레지스트리에 없는 폴더는 `{미배정}`으로 표시되어 나중에 aliases 한 줄 추가로 흡수할 수 있습니다. config가 없으면 기존 폴더명 태그 동작이 그대로 유지됩니다. 스키마·해석 규칙은 `agents/_shared/config-contract.md` 참조.
```

- [ ] **Step 6: 정합성 검토 후 Commit** — 전체 재독: Phase 0↔Phase 1.5(전일 참조)↔Phase 1 순서 무모순, CRITICAL 규칙 충돌 없음, agent.json 파싱 확인(`python -c "import json;json.load(open('agents/workflow/daily-work-reporter/agent.json',encoding='utf-8'))"`)

```bash
git add agents/workflow/daily-work-reporter/
git commit -m "feat: add config registry resolution (Phase 0) to daily-work-reporter"
```

---

### Task 4: weekly-work-reporter Phase 0 (v1.5.0)

**Files:**
- Modify: `agents/workflow/weekly-work-reporter/weekly-work-reporter.md`
- Modify: `agents/workflow/weekly-work-reporter/agent.json`
- Modify: `agents/workflow/weekly-work-reporter/README.md`

**Interfaces:**
- Consumes: Task 1 계약 §4(weekly 행)·§5(핸드오프), Task 2 CLI(`--config <json>`)와 meta 키(config_loaded/unregistered_projects/excluded_count)

- [ ] **Step 1: Phase 0 블록 삽입** — `### Phase 1: 대상 주 결정 및 파일 탐색` 라인 **바로 앞**에 삽입:

```markdown
### Phase 0: 설정 로드 & 프로젝트 해석 (공통, 선택적)

0-1. **설정 정본 로드**
   - `mcp__obsidian__obsidian_get_file_contents`로 `_config/work-agents.yaml` 읽기 시도
   - 실패(404/연결 오류/YAML 파싱 불가) 시: **이 Phase 전체를 조용히 생략**하고 기존 동작 유지 (후위호환)

0-2. **설정 파싱**
   - `paths`/`projects`(레지스트리)/`rules`/`vocab` 추출
   - `paths.daily_dir`/`paths.weekly_dir`가 있으면 각각 일일/주간 디렉토리 경로로 사용

0-3. **프로젝트 해석 규칙 (그룹핑 0단계)**
   - 모든 프로젝트 판정의 **최상단**에 registry 정규화 적용: 원시 태그/헤더/키워드를 정규화(소문자·공백·구두점 무시)하여 레지스트리 id/name/aliases와 대조 → 일치 시 **표시명(name)**으로 통일 (차트 라벨 파편화 종결)
   - 레지스트리에 없는 태그는 **원시 철자 그대로 유지**(미등록) — 보고서 하단 보강 제안에서 "미등록 프로젝트 태그: X, Y — aliases 추가로 흡수 가능" 안내
   - 상세 알고리즘 정본: `agents/_shared/config-contract.md` (수정 시 4개 에이전트 lockstep)

0-4. **스크립트 핸드오프 준비**
   - 5-0 결정적 집계 실행 시: 읽은 YAML을 구조 그대로 canonical JSON으로 직렬화해 임시 디렉토리에 `work-agents.json`으로 저장 → `--config` 인자로 전달
   - 스크립트가 정규화·가감(exclude_keywords/always_include)을 수치 레벨에서 적용하므로, 스크립트 성공 시 **정규화 결과도 스크립트 출력이 정본**
```

- [ ] **Step 2: 5-0 단계에 --config 연결** — 5-0 블록의 실행 라인:
```
   - 실행: `python aggregate_weekly.py --dir <임시디렉토리> --week-start <월요일> --week-end <금요일> [--prev-weekly <전주보고서 임시파일>]` (`python` 실패 시 `python3` 재시도)
```
을 다음으로 교체:
```
   - 실행: `python aggregate_weekly.py --dir <임시디렉토리> --week-start <월요일> --week-end <금요일> [--prev-weekly <전주보고서 임시파일>] [--config <work-agents.json>]` (`python` 실패 시 `python3` 재시도; `--config`는 Phase 0 성공 시에만 부여)
```
그리고 5-0의 "성공 시" 목록 끝에 불릿 추가:
```
     * `meta.unregistered_projects`가 비어있지 않으면 보강 제안 단계에서 사용자에게 미등록 태그 목록과 aliases 추가 방법 안내
```

- [ ] **Step 3: 그룹핑 cascade 0단계 추가** — `6. **프로젝트별 그룹핑** (핵심 로직)`의 그룹핑 우선순위 목록 첫 항목(`1. **항목 인라인 ...`) **바로 앞**에 추가:

```markdown
     0. **(Phase 0 성공 시) registry 정규화**: 아래 1~5로 얻은 원시 프로젝트명을 레지스트리 id/name/aliases와 정규화 대조 → 일치 시 표시명(name)으로 치환 (alias 흡수). 미일치 시 원시명 유지(미등록)
```

그리고 `## 프로젝트 그룹핑 규칙` 섹션의 `### 카테고리 기반 보고서 처리` 목록 첫 항목 앞에도 동일한 0단계 한 줄을 추가:
```markdown
0. **(config 로드 성공 시) registry 정규화** — 아래 모든 단계의 결과를 레지스트리 aliases로 흡수해 표시명으로 통일 (`agents/_shared/config-contract.md` 참조)
```

- [ ] **Step 4: Starting Instructions 갱신** — 목록에서 1번 앞에 0번 추가:
```markdown
0. `_config/work-agents.yaml` 로드 시도 (Phase 0) — 성공 시 registry 정규화 활성 + YAML을 JSON으로 직렬화해 6단계 스크립트에 `--config`로 전달, 실패 시 조용히 생략
```
그리고 기존 6번(결정적 집계 실행) 항목의 괄호를 `(배포 경로 → 리포 경로 순, 전주 보고서 확보 시 --prev-weekly, Phase 0 성공 시 --config 전달)`로 교체.

- [ ] **Step 5: agent.json + README**

`"version": "1.4.0"` → `"version": "1.5.0"`, capabilities 끝에 추가:
```json
"vault _config/work-agents.yaml 레지스트리 연동 — alias 흡수로 프로젝트 라벨 파편화 종결, 차트 라벨=표시명 (config 부재 시 기존 동작)",
"config 가감 규칙(per_project exclude_keywords/always_include)의 수치 레벨 적용 (aggregate_weekly.py --config)",
"미등록 프로젝트 태그 감지 및 레지스트리 보강 안내 (meta.unregistered_projects)"
```

README: `### 결정적 집계 스크립트 (v1.4.0)` 섹션 뒤에 문단 추가 + Version History `### v1.5.0` 행 추가:
```markdown
### 프로젝트 레지스트리 연동 (v1.5.0)

vault `_config/work-agents.yaml`의 프로젝트 레지스트리(id/name/aliases)를 로드해 일일보고의 다양한 프로젝트 철자(`{RAMS}`, `{ramsa}`, `{ATL-RAMS ALE}` 등)를 하나의 표시명으로 정규화합니다. 정규화·가감은 집계 스크립트(`--config`)가 수치 레벨에서 수행하므로 차트와 통계가 일관됩니다. 레지스트리에 없는 태그는 원시 철자를 유지하고 보강 제안에서 안내합니다. config가 없으면 기존 동작이 그대로 유지됩니다.
```

- [ ] **Step 6: 정합성 검토 후 Commit** — 전체 재독(Phase 0↔5-0↔그룹핑 0단계 무모순, "차트 수치 임의 수정 금지" CRITICAL과 정합), agent.json 파싱 확인

```bash
git add agents/workflow/weekly-work-reporter/
git commit -m "feat: add config registry normalization (Phase 0) to weekly-work-reporter"
```

---

### Task 5: pm-board-manager Phase 0 (v1.1.0)

**Files:**
- Modify: `agents/workflow/pm-board-manager/pm-board-manager.md`
- Modify: `agents/workflow/pm-board-manager/agent.json`
- Modify: `agents/workflow/pm-board-manager/README.md`

**Interfaces:**
- Consumes: Task 1 계약 §4(pm-board 행): thresholds 매핑(stall_days→정체임계일, wip_limit→WIP임계, promise_window→약속 미이행 판정 영업일), registry milestones/deadline 우선

- [ ] **Step 1: 공통 Phase 0 삽입 + 기존 Phase 0 개명** — 기존 `### Phase 0: 컨텍스트 확인 (실행 모드 판별)` 라인을 `### Phase 0.5: 컨텍스트 확인 (실행 모드 판별)`로 개명하고(내부 스텝 1~2 번호는 무변경), 그 **바로 앞**에 삽입:

```markdown
### Phase 0: 설정 로드 & 프로젝트 해석 (공통, 선택적)

0-1. **설정 정본 로드**
   - `mcp__obsidian__obsidian_get_file_contents`로 `_config/work-agents.yaml` 읽기 시도
   - 실패(404/연결 오류/YAML 파싱 불가) 시: **이 Phase 전체를 조용히 생략**하고 기존 동작 유지 (후위호환)

0-2. **설정 파싱 및 적용**
   - `paths.pm_board`가 있으면 보드 파일 경로로 사용 (없으면 기존 `PM보드/PM-Board.md`)
   - **thresholds 우선순위**: `rules.thresholds`의 `stall_days`(정체임계일)·`wip_limit`(WIP임계)·`promise_window`(약속 미이행 판정 영업일)를 **보드 frontmatter `config` 값보다 우선** 적용 (둘 다 없으면 기존 기본값 3/8/3)
   - **마일스톤·마감**: 레지스트리 `projects[].milestones`/`deadline`이 있으면 보드 frontmatter `milestones`·추론보다 **우선** 사용

0-3. **프로젝트 해석 규칙 (포트폴리오 집계)**
   - 일일/주간보고에서 얻은 프로젝트명(인라인 `{태그}`·H2·키워드)을 정규화(소문자·공백·구두점 무시)해 레지스트리 id/name/aliases와 대조 → **id 기준으로 집계**하고 표에는 **표시명(name)** 표기 (철자 변형이 한 행으로 합쳐짐)
   - 레지스트리에 없는 이름은 원시 철자 유지, `status: dormant` 프로젝트는 활동이 없으면 휴면 표기에 참고
   - 상세 알고리즘 정본: `agents/_shared/config-contract.md` (수정 시 4개 에이전트 lockstep)
```

- [ ] **Step 2: 관련 규칙 라인 갱신**

Quality Guidelines 일관성 항목:
```
- config(정체임계일/WIP임계)는 보드 frontmatter 값을 우선 사용, 없으면 기본값(3/8)
```
을 다음으로 교체:
```
- 임계값 우선순위: `_config/work-agents.yaml`의 `rules.thresholds` > 보드 frontmatter `config` > 기본값(정체임계일 3 / WIP임계 8 / 약속판정 3영업일)
```

7단계(약속 이행 추적)의 `* 미이행: N영업일(기본 3) 경과하도록 어디에도 무언급` 라인을 다음으로 교체:
```
     * `미이행`: N영업일(기본 3, config `rules.thresholds.promise_window` 우선) 경과하도록 어디에도 무언급
```

11단계(포트폴리오 집계)의 마일스톤 불릿:
```
    - **마일스톤**: 이전 보드나 frontmatter에 사용자가 명시한 마일스톤이 있으면 그것을 **우선 사용**, 없으면 주간보고 Executive Summary·"다음 주 계획"의 큰 항목에서 추론
```
을 다음으로 교체:
```
    - **마일스톤**: config 레지스트리 `projects[].milestones`/`deadline` > 이전 보드·frontmatter 명시 > 주간보고 Executive Summary·"다음 주 계획" 추론 순으로 사용
```

Starting Instructions 목록에서 1번 앞에 0번 추가:
```markdown
0. `_config/work-agents.yaml` 로드 시도 (Phase 0) — 성공 시 thresholds/마일스톤/레지스트리 집계 활성, 실패 시 조용히 생략
```
그리고 Starting Instructions 3번 항목의 `(가장 먼저)`를 `(설정 로드 다음, 소스 수집 전)`으로 교체 (신규 0번과의 순서 충돌 제거).

- [ ] **Step 3: agent.json + README**

`"version": "1.0.0"` → `"version": "1.1.0"`, capabilities 끝에 추가:
```json
"vault _config/work-agents.yaml 연동 — thresholds(정체임계일·WIP임계·약속판정) config 우선 적용, 포트폴리오를 레지스트리 id 기준 집계·표시명 표기",
"레지스트리 projects[].milestones/deadline을 마일스톤 추론보다 우선 사용"
```

README: 기능 문단 + Version History `### v1.1.0` 행 추가:
```markdown
### 프로젝트 레지스트리 연동 (v1.1.0)

vault `_config/work-agents.yaml`이 있으면 정체임계일·WIP임계·약속판정 기준을 config에서 읽고(보드 frontmatter보다 우선), 포트폴리오 보드를 레지스트리 id 기준으로 집계해 프로젝트 철자 변형이 한 행으로 합쳐집니다. 레지스트리의 마일스톤·마감일이 추론보다 우선합니다. config가 없으면 기존 동작 그대로입니다. 스키마는 `agents/_shared/config-contract.md` 참조.
```

- [ ] **Step 4: 정합성 검토 후 Commit** — 전체 재독(Phase 0/0.5 순서·명명 일관, 시간축 비교 원칙과 무충돌), agent.json 파싱 확인

```bash
git add agents/workflow/pm-board-manager/
git commit -m "feat: add config registry and thresholds (Phase 0) to pm-board-manager"
```

---

### Task 6: project-wbs-gantt-designer Phase 0 (v1.1.0)

**Files:**
- Modify: `agents/workflow/project-wbs-gantt-designer/project-wbs-gantt-designer.md`
- Modify: `agents/workflow/project-wbs-gantt-designer/agent.json`
- Modify: `agents/workflow/project-wbs-gantt-designer/README.md`

**Interfaces:**
- Consumes: Task 1 계약 §4(wbs-gantt 행): 프로젝트명 registry 검증, deadline/milestones 자동 주입, 인라인 태그 resolve

- [ ] **Step 1: Phase 0 삽입** — `### Phase 1: 프로젝트 식별 & 범위 확보` 라인 **바로 앞**에 삽입:

```markdown
### Phase 0: 설정 로드 & 프로젝트 해석 (공통, 선택적)

0-1. **설정 정본 로드**
   - `mcp__obsidian__obsidian_get_file_contents`로 `_config/work-agents.yaml` 읽기 시도
   - 실패(404/연결 오류/YAML 파싱 불가) 시: **이 Phase 전체를 조용히 생략**하고 기존 동작 유지 (후위호환)

0-2. **설정 파싱**
   - `paths.wbs_dir`가 있으면 산출물 디렉토리 경로로 사용 (없으면 기존 `프로젝트관리`)
   - 레지스트리 `projects[]`(id/name/aliases/deadline/milestones) 추출

0-3. **프로젝트 해석 규칙**
   - 사용자 입력 프로젝트명을 정규화(소문자·공백·구두점 무시)해 레지스트리 id/name/aliases와 대조:
     * **일치**: 표시명(name)을 공식 프로젝트명으로 확정 (파일명·frontmatter `project`·H1에 사용). 레지스트리에 `deadline`/`milestones`가 있으면 **자동 주입**하여 Phase 1의 해당 질문 생략
     * **미일치**: "레지스트리에 없는 프로젝트입니다. 이 이름 그대로 진행할까요? (`_config/work-agents.yaml`에 등록하면 보고서 자동 매칭이 좋아집니다)" 확인 후 자유 텍스트로 진행 (기존 동작)
   - 보고서 항목 선별(Phase 1의 프로젝트 그룹핑)에서 항목 인라인 `{태그}`도 레지스트리로 정규화해 대조 — alias 철자 변형이 있어도 대상 프로젝트 작업으로 수집됨
   - 상세 알고리즘 정본: `agents/_shared/config-contract.md` (수정 시 4개 에이전트 lockstep)
```

- [ ] **Step 2: Phase 1 그룹핑·질문 단계 갱신**

3단계의 프로젝트 그룹핑 우선순위 목록:
```
   - **프로젝트 그룹핑** (우선순위):
     1. 프로젝트 기반 H2 헤더(예: `## ATL AXIS Frontend`)
     2. frontmatter `project`/`focus_project` 필드
     3. 항목 괄호 원문/제목의 프로젝트 키워드
```
을 다음으로 교체:
```
   - **프로젝트 그룹핑** (우선순위):
     1. 항목 인라인 `{프로젝트}` 태그 (daily-work-reporter 자동 부착 — 가장 구체적)
     2. 프로젝트 기반 H2 헤더(예: `## ATL AXIS Frontend`)
     3. frontmatter `project`/`focus_project` 필드
     4. 항목 괄호 원문/제목의 프로젝트 키워드
   - (Phase 0 성공 시) 위 1~4로 얻은 원시명을 레지스트리로 정규화하여 대상 프로젝트와 대조 (alias 흡수)
```

5단계(누락 정보 확보)의 마감일 불릿:
```
   - 마감일을 알 수 없으면: 사용자에게 반드시 질문 (간트 일정 배분의 기준)
```
을 다음으로 교체:
```
   - 마감일을 알 수 없으면: 레지스트리 `deadline`이 주입된 경우 그 값을 사용(질문 생략), 없으면 사용자에게 반드시 질문 (간트 일정 배분의 기준)
```

Starting Instructions 목록에서 1번 앞에 0번 추가:
```markdown
0. `_config/work-agents.yaml` 로드 시도 (Phase 0) — 성공 시 프로젝트명 registry 검증 + deadline/milestones 자동 주입, 실패 시 조용히 생략
```

- [ ] **Step 3: agent.json + README**

`"version": "1.0.0"` → `"version": "1.1.0"`, capabilities 끝에 추가:
```json
"vault _config/work-agents.yaml 연동 — 프로젝트명 레지스트리 검증·표시명 확정, deadline/milestones 자동 주입으로 질문 감소",
"인라인 {프로젝트} 태그 + alias 정규화 기반 보고서 항목 선별 정확도 향상"
```

README: 기능 문단 + Version History `### v1.1.0` 행 추가:
```markdown
### 프로젝트 레지스트리 연동 (v1.1.0)

vault `_config/work-agents.yaml`이 있으면 사용자가 말한 프로젝트명을 레지스트리로 검증해 공식 표시명으로 확정하고, 등록된 마감일·마일스톤을 자동 주입해 질문을 줄입니다. 보고서 항목 선별 시 인라인 `{프로젝트}` 태그와 alias 정규화를 사용해 철자 변형에도 작업을 정확히 수집합니다. config가 없으면 기존 동작 그대로입니다.
```

- [ ] **Step 4: 정합성 검토 후 Commit** — 전체 재독(Phase 0↔Phase 1 질문 흐름 무모순, "마감일 임의 단정 금지"와 정합 — registry 주입은 사용자 정의 값이므로 단정이 아님), agent.json 파싱 확인

```bash
git add agents/workflow/project-wbs-gantt-designer/
git commit -m "feat: add config registry validation (Phase 0) to project-wbs-gantt-designer"
```

---

### Task 7: 전체 검증 + vault config 생성 + lockstep 배포

(컨트롤러가 직접 수행하는 검증·배포 태스크)

**Files:**
- Create (vault, via Obsidian MCP): `_config/work-agents.yaml` (Task 1 샘플과 동일 내용)
- Modify (배포본): `~/.claude/agents/{daily,weekly,pm-board-manager,project-wbs-gantt-designer}.md`, `~/.claude/agent-scripts/weekly-work-reporter/aggregate_weekly.py`

- [ ] **Step 1: 전체 테스트** — `python -m pytest agents/workflow/weekly-work-reporter/scripts/ -v` → 29건 PASS
- [ ] **Step 2: 스펙·플랜 문서 커밋** — `git add docs/superpowers/specs/2026-06-15-work-agents-config-monitoring-platform-design.md docs/superpowers/plans/2026-07-06-config-core-phase1.md` 후 `docs:` 커밋 (2026-06-15 스펙이 B안의 정본이므로 이 시점에 리포에 수록)
- [ ] **Step 3: 최종 브랜치 리뷰** (subagent-driven-development 최종 리뷰 절차)
- [ ] **Step 4: vault config 생성** — Obsidian MCP `obsidian_append_content`로 `_config/work-agents.yaml`에 샘플 내용 기록 (이미 존재하면 덮어쓰지 않고 사용자 확인)
- [ ] **Step 5: 배포** — `& .\scripts\sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter,pm-board-manager,project-wbs-gantt-designer -Apply -All` → 재실행 리포트 전 항목 IDENTICAL 확인
- [ ] **Step 6: 스모크** — 배포본 스크립트를 `--config fixtures/config.json`으로 실행해 `"결제 서비스"` 라벨 확인
- [ ] **Step 7: 병합 옵션 제시** (finishing-a-development-branch)
