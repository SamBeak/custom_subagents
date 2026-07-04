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


def test_quoted_frontmatter_status_recognized(tmp_path):
    # frontmatter status가 따옴표로 감싸여도(confirmed) 정상 인식되어야 한다
    (tmp_path / "2026-06-22.md").write_text(
        '---\nstatus: "confirmed"\n---\n\n## 오늘 한 일\n\n- **결제 모듈 개발** `30/100%`\n',
        encoding="utf-8")
    r = agg.aggregate(str(tmp_path), week_start="2026-06-22", week_end="2026-06-22")
    assert r["stats"]["confirmed_reports"] == 1
    assert r["meta"]["confirmed_dates"] == ["2026-06-22"]


def test_cli_outputs_valid_json():
    out = subprocess.run(
        [sys.executable, str(Path(agg.__file__)), "--dir", str(DAILY),
         "--week-start", "2026-06-22", "--week-end", "2026-06-26"],
        capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0
    assert json.loads(out.stdout)["stats"]["done"] == 3
