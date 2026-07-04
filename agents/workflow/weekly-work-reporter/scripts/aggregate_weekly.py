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

DATE_FILE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.md$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FRONTMATTER_KV_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOP_BULLET_RE = re.compile(r"^- (.+)$")
SUB_BULLET_RE = re.compile(r"^\s+- (.+)$")
PAREN_LINE_RE = re.compile(r"^\((.+)\)$")
PREV_DONE_RE = re.compile(r"완료 업무:\s*(\d+)\s*건")


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


def guess_category(title, tech_term=None):
    """태그 부재 시 키워드 휴리스틱 (weekly 프롬프트 7-2와 동일 키워드·우선순위)."""
    text = f"{title} {tech_term or ''}"
    for tag, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keywords):
            return tag
    return "기타"


def parse_frontmatter(text):
    """첫 --- 쌍 내부의 key: value 추출. (frontmatter dict, 본문) 반환."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        kv = FRONTMATTER_KV_RE.match(line)
        if kv:
            fm[kv.group(1)] = kv.group(2)
    return fm, text[m.end():]


def parse_item_line(line):
    """최상위 불릿 1줄 파싱. ITEM_RE 불일치 시 None (unparsed 대상)."""
    m = ITEM_RE.match(line)
    if not m:
        return None
    tag, title, rest = m.group(1), m.group(2).strip(), m.group(3)
    pm = TOKEN_PROGRESS.search(rest)
    pj = TOKEN_PROJECT.search(rest)
    hm = TOKEN_HOURS.search(rest)
    prm = TOKEN_PRIORITY.search(rest)
    hours = None
    if hm:
        hours = float(hm.group(1)) * (8.0 if hm.group(2) == "d" else 1.0)
    return {
        "tag": tag,
        "title": title,
        "pct": int(pm.group(1)) if pm else None,
        "inline_project": pj.group(1) if pj else None,
        "hours": hours,
        "priority": prm.group(1) if prm else None,
        "sub_bullets": [],
    }


def classify_sub_bullets(sub_bullets):
    """하위 불릿 분류 → (식별자 목록, 설명 불릿 수, 원문 기술 용어 or None)."""
    identifiers = []
    others = []
    for s in sub_bullets:
        if IDENTIFIER_RE.match(s):
            identifiers.append(s[1:-1].strip())
        else:
            others.append(s)
    tech_term = None
    if others:
        pm = PAREN_LINE_RE.match(others[-1])
        if pm:
            tech_term = pm.group(1).strip()
            others = others[:-1]
    return identifiers, len(others), tech_term


def parse_daily(text, day_str):
    """일일보고 1건 파싱 → (frontmatter, 항목 리스트, unparsed 리스트)."""
    fm, body = parse_frontmatter(text)
    items = []
    unparsed = []
    section = None
    is_project_section = False
    current = None
    for line in body.splitlines():
        hm = HEADING_RE.match(line)
        if hm:
            if len(hm.group(1)) == 2:
                section = hm.group(2)
                is_project_section = section not in CATEGORY_SECTIONS
            current = None
            continue
        sm = SUB_BULLET_RE.match(line)
        if sm:
            if current is not None:
                current["sub_bullets"].append(sm.group(1).strip())
            continue
        if TOP_BULLET_RE.match(line) and section is not None:
            item = parse_item_line(line)
            if item is None:
                unparsed.append({"date": day_str, "section": section, "text": line})
                current = None
            else:
                item["section"] = section
                item["is_project_section"] = is_project_section
                items.append(item)
                current = item
    return fm, items, unparsed


def parse_prev_weekly(path):
    """전주 주간보고 파싱 → (병합 키 집합 or None, 전주 완료 건수 or None).

    키 출처: '진행 중'(프로젝트 하위 H4)·'다음 주 계획' 섹션 항목.
    파싱 실패(키 0건)면 키 집합 None (추정 금지).
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None, None
    keys = set()
    prev_done = None
    collect = False
    in_stats = False
    current_title = None
    current_subs = []

    def flush():
        nonlocal current_title, current_subs
        if current_title is not None:
            _, _, term = classify_sub_bullets(current_subs)
            keys.add(normalize_key(term or current_title))
        current_title, current_subs = None, []

    for line in text.splitlines():
        hm = HEADING_RE.match(line)
        if hm:
            flush()
            heading = hm.group(2)
            collect = heading == "진행 중" or heading.startswith("다음 주 계획")
            in_stats = heading.startswith("주간 통계")
            continue
        if in_stats:
            dm = PREV_DONE_RE.search(line)
            if dm:
                prev_done = int(dm.group(1))
            continue
        if not collect:
            continue
        im = ITEM_RE.match(line)
        if im:
            flush()
            current_title = im.group(2).strip()
            continue
        sm = SUB_BULLET_RE.match(line)
        if sm and current_title is not None:
            current_subs.append(sm.group(1).strip())
    flush()
    return (keys if keys else None), prev_done


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
    # ---- 파일 수집 + 날짜 범위·주말 필터 ----
    dir_path = Path(daily_dir)
    dated_files = {}
    for p in sorted(dir_path.glob("*.md")):
        fm_match = DATE_FILE_RE.match(p.name)
        if not fm_match:
            continue
        try:
            d = date(int(fm_match.group(1)), int(fm_match.group(2)), int(fm_match.group(3)))
        except ValueError:
            continue
        dated_files[d] = p
    ws = date.fromisoformat(week_start) if week_start else (min(dated_files) if dated_files else None)
    we = date.fromisoformat(week_end) if week_end else (max(dated_files) if dated_files else None)
    selected = [(d, p) for d, p in sorted(dated_files.items())
                if (ws is None or d >= ws) and (we is None or d <= we)
                and (include_weekends or d.weekday() < 5)]

    # ---- 일자별 파싱 + 병합 ----
    days_out = []
    analyzed_dates = []
    confirmed_dates = []
    draft_dates = []
    unparsed_all = []
    tomorrow_plans = []
    merged_index = {}   # key -> 내부 병합 dict
    merged_order = []

    for d, p in selected:
        day_str = d.isoformat()
        fm, items, unparsed = parse_daily(p.read_text(encoding="utf-8"), day_str)
        analyzed_dates.append(day_str)
        unparsed_all.extend(unparsed)
        status = fm.get("status", "").strip().lower()
        if status == "confirmed":
            confirmed_dates.append(day_str)
        elif status == "draft":
            draft_dates.append(day_str)
        else:
            status = "none"
        fm_project = fm.get("project") or fm.get("focus_project")

        item_count = 0
        completed_count = 0
        for item in items:
            identifiers, desc_count, tech_term = classify_sub_bullets(item["sub_bullets"])
            # 프로젝트 판정: 인라인 태그 > 프로젝트 H2 > frontmatter > 일반 업무
            if item["inline_project"]:
                project = item["inline_project"]
            elif item["is_project_section"]:
                project = item["section"]
            elif fm_project:
                project = fm_project
            else:
                project = "일반 업무"

            if item["section"] == "내일 할 일":
                tomorrow_plans.append({
                    "date": day_str,
                    "title": item["title"],
                    "project": project,
                    "category": item["tag"] or guess_category(item["title"], tech_term),
                })
                continue
            if item["section"] == "특이사항":
                continue

            # 처리 건수 대상: 오늘 한 일 + 진행 중인 일 + 프로젝트 H2 항목
            item_count += 1
            if item["pct"] == 100:
                completed_count += 1

            key = normalize_key(tech_term or item["title"])
            entry = merged_index.get(key)
            if entry is None:
                entry = {
                    "key": key,
                    "title": item["title"],
                    "tech_term": None,
                    "explicit_project": None,
                    "fallback_project": project,
                    "explicit_tag": None,
                    "first_date": day_str,
                    "last_date": day_str,
                    "dates": set(),
                    "start_pct": None,
                    "end_pct": None,
                    "hours_sum": 0.0,
                    "has_hours": False,
                    "priority": None,
                    "identifiers": [],
                    "max_desc_bullets": 0,
                    "last_section": item["section"],
                }
                merged_index[key] = entry
                merged_order.append(key)
            entry["title"] = item["title"]
            entry["last_date"] = day_str
            entry["dates"].add(day_str)
            entry["last_section"] = item["section"]
            entry["fallback_project"] = project
            if item["inline_project"]:
                entry["explicit_project"] = item["inline_project"]
            if item["tag"]:
                entry["explicit_tag"] = item["tag"]
            if tech_term:
                entry["tech_term"] = tech_term
            if item["pct"] is not None:
                if entry["start_pct"] is None:
                    entry["start_pct"] = item["pct"]
                entry["end_pct"] = item["pct"]
            if item["hours"] is not None:
                entry["hours_sum"] += item["hours"]
                entry["has_hours"] = True
            if item["priority"]:
                entry["priority"] = item["priority"]
            for ident in identifiers:
                if ident not in entry["identifiers"]:
                    entry["identifiers"].append(ident)
            entry["max_desc_bullets"] = max(entry["max_desc_bullets"], desc_count)

        days_out.append({
            "date": day_str,
            "weekday_kr": WEEKDAY_KR[d.weekday()],
            "item_count": item_count,
            "completed_count": completed_count,
            "status": status,
        })

    # ---- 이월(carryover) 판정 ----
    prev_keys = None
    prev_done = None
    if prev_weekly:
        prev_keys, prev_done = parse_prev_weekly(prev_weekly)

    # ---- 병합 확정 + 공수 점수 ----
    merged_out = []
    proj_scores = {}
    proj_done = {}
    proj_wip = {}
    cat_scores = {}
    cat_counts = {}
    for key in merged_order:
        e = merged_index[key]
        internal = {
            "title": e["title"],
            "tech_term": e["tech_term"],
            "days_seen": len(e["dates"]),
            "start_pct": e["start_pct"],
            "end_pct": e["end_pct"],
            "hours_total": e["hours_sum"] if e["has_hours"] else None,
            "max_desc_bullets": e["max_desc_bullets"],
        }
        score = effort_score(internal)
        project = e["explicit_project"] or e["fallback_project"]
        category = e["explicit_tag"] or guess_category(e["title"], e["tech_term"])
        completed = e["end_pct"] == 100
        merged_out.append({
            "key": key,
            "title": e["title"],
            "tech_term": e["tech_term"],
            "project": project,
            "category": category,
            "first_date": e["first_date"],
            "last_date": e["last_date"],
            "days_seen": internal["days_seen"],
            "start_pct": e["start_pct"],
            "end_pct": e["end_pct"],
            "completed": completed,
            "hours_total": internal["hours_total"],
            "priority": e["priority"],
            "identifiers": e["identifiers"],
            "carryover": (key in prev_keys) if prev_keys is not None else None,
            "last_section": e["last_section"],
        })
        proj_scores[project] = proj_scores.get(project, 0.0) + score
        proj_done[project] = proj_done.get(project, 0) + (1 if completed else 0)
        proj_wip[project] = proj_wip.get(project, 0) + (0 if completed else 1)
        cat_scores[category] = cat_scores.get(category, 0.0) + score
        cat_counts[category] = cat_counts.get(category, 0) + 1

    # ---- projects / categories ----
    proj_pcts = normalize_pcts(proj_scores)
    projects_out = []
    for name in sorted(proj_scores, key=lambda k: (-proj_scores[k], k)):
        done_n, wip_n = proj_done[name], proj_wip[name]
        total_n = done_n + wip_n
        completion_pct = round(done_n / total_n * 10) * 10 if total_n else 0
        projects_out.append({
            "name": name,
            "effort_score": round(proj_scores[name], 2),
            "effort_pct": proj_pcts[name],
            "done_count": done_n,
            "wip_count": wip_n,
            "completion_pct": completion_pct,
            "bar": pct_bar(completion_pct),
        })

    cat_pcts = normalize_pcts(cat_scores)
    categories_out = [
        {"tag": tag, "label_kr": LABELS_KR.get(tag, tag),
         "pct": cat_pcts[tag], "count": cat_counts[tag]}
        for tag in sorted(cat_scores, key=lambda k: (-cat_scores[k], k))
    ]

    # ---- meta ----
    missing_weekdays = []
    if ws is not None and we is not None:
        cursor = ws
        while cursor <= we:
            if cursor.weekday() < 5 and cursor.isoformat() not in analyzed_dates:
                missing_weekdays.append(cursor.isoformat())
            cursor += timedelta(days=1)
    if ws is not None:
        iso = ws.isocalendar()
        iso_week = f"{iso[0]}-W{iso[1]:02d}"
    else:
        iso_week = None
    meta = {
        "week_start": ws.isoformat() if ws else None,
        "week_end": we.isoformat() if we else None,
        "iso_week": iso_week,
        "analyzed_dates": analyzed_dates,
        "missing_weekdays": missing_weekdays,
        "confirmed_dates": confirmed_dates,
        "draft_dates": draft_dates,
        "unparsed_count": len(unparsed_all),
    }

    # ---- stats ----
    done = sum(1 for m in merged_out if m["completed"])
    wip = len(merged_out) - done
    if prev_keys is not None:
        carried_in = sum(1 for m in merged_out if m["carryover"])
        new_started = sum(1 for m in merged_out if m["carryover"] is False)
    else:
        carried_in = None
        new_started = len(merged_out)  # 주 내 기준: 해당 주 최초 등장
    prev_week = None
    if prev_done is not None:
        prev_week = {"done": prev_done, "wow_done_delta": done - prev_done}
    stats = {
        "done": done,
        "wip": wip,
        "new_started": new_started,
        "carried_in": carried_in,
        "carry_next": wip,
        "confirmed_reports": len(confirmed_dates),
        "total_reports": len(analyzed_dates),
        "prev_week": prev_week,
    }

    # ---- charts ----
    project_pie = mermaid_pie(f"프로젝트별 공수 배분 ({iso_week})",
                              normalize_pcts(fold_small_groups(proj_scores)))
    cat_labeled = {}
    for tag, score in fold_small_groups(cat_scores).items():
        label = tag if tag not in LABELS_KR else f"{LABELS_KR[tag]} [{tag}]"
        cat_labeled[label] = score
    category_pie = mermaid_pie(f"업무 유형별 비중 ({iso_week})", normalize_pcts(cat_labeled))

    counts = [day["item_count"] for day in days_out]
    max_count = max(counts) if counts else 0
    unit = max(1, math.ceil(max_count / 10))
    trend_lines = ["| 날짜 | 요일 | 처리 건수 | 시각화 |", "|------|------|-----------|--------|"]
    for day in days_out:
        dd = date.fromisoformat(day["date"])
        trend_lines.append(f"| {dd.strftime('%m-%d')} | {day['weekday_kr']} | "
                           f"{day['item_count']}건 | {count_bar(day['item_count'], unit)} |")
    avg = sum(counts) / len(counts) if counts else 0.0
    missing_txt = ", ".join(missing_weekdays) if missing_weekdays else "없음"
    trend_lines.append("")
    trend_lines.append(f"> 한 칸 = {unit}건 환산. 누락 일자: {missing_txt}. 평균 약 {avg:.1f}건/일.")
    daily_trend_table = "\n".join(trend_lines)

    comp_lines = ["| 프로젝트 | 완료 | 진행 중 | 완료율 시각화 |", "|---|---|---|---|"]
    for proj in sorted(projects_out,
                       key=lambda x: (-x["completion_pct"], -x["effort_score"], x["name"])):
        comp_lines.append(f"| {proj['name']} | {proj['done_count']} | {proj['wip_count']} | "
                          f"{proj['bar']} {proj['completion_pct']}% |")
    comp_lines.append("")
    comp_lines.append("> 완료율 = 완료 / (완료 + 진행 중) × 100, 10% 단위 반올림. 완료율 내림차순 정렬.")
    completion_table = "\n".join(comp_lines)

    charts = {
        "project_pie": project_pie,
        "category_pie": category_pie,
        "daily_trend_table": daily_trend_table,
        "completion_table": completion_table,
    }

    return {
        "meta": meta,
        "days": days_out,
        "merged": merged_out,
        "tomorrow_plans": tomorrow_plans,
        "projects": projects_out,
        "categories": categories_out,
        "charts": charts,
        "stats": stats,
        "unparsed": unparsed_all,
    }


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
