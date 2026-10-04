#!/usr/bin/env python3
"""Поиск вакансий без браузера и без ключей: борды компаний (ATS) + открытые remote-доски.

Что обходит (список включается в me/profile.yaml -> search.sources):
    ats       — борды компаний из config/ats_orgs.txt (Ashby, Greenhouse, Lever, Workable,
                Recruitee). Самый ценный источник: ссылка сразу ведёт на настоящую форму,
                дата и гео — от самой компании.
    jobicy    — jobicy.com, remote-вакансии с регионом.
    remoteok  — remoteok.com.
    remotive  — remotive.com.

Фильтры — из профиля: название роли (search.title_include / title_exclude), свежесть
(search.max_age_days), гео (geo.ok_keywords / block_keywords), компании-исключения.
Гео здесь ПРЕДВАРИТЕЛЬНОЕ: «Remote» на доске часто значит одну страну. Перед подачей
текст вакансии и форму всё равно читаем на сайте компании (CLAUDE.md -> «Отбор»).

Журнал data/seen.json: повторный прогон показывает только новое.

Запуск:
    python scripts/scan.py                 # новое с прошлого раза
    python scripts/scan.py --all           # весь свежий срез, без журнала
    python scripts/scan.py --days 7        # своё окно свежести
    python scripts/scan.py --only ats      # один источник
    python scripts/scan.py --to-tracker    # записать новое в трекер статусом found
Результат: data/scan_latest.json + таблица в консоли.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import kit  # noqa: E402

ORGS = kit.ROOT / "config" / "ats_orgs.txt"
SEEN = kit.DATA / "seen.json"
OUT = kit.DATA / "scan_latest.json"
ENGINES = ("ashby", "greenhouse", "lever", "workable", "recruitee")


# ── источники: каждый отдаёт список {company, title, location, url, age_days, source} ──

def load_orgs() -> list[tuple[str, str]]:
    out = []
    if not ORGS.exists():
        return out
    for line in ORGS.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        parts = line.split()
        if len(parts) == 2 and parts[0] in ENGINES:
            out.append((parts[0], parts[1]))
        elif line:
            print(f"  ! ats_orgs: пропускаю «{line}» — движок не из {ENGINES}", file=sys.stderr)
    return out


def fetch_org(ats: str, org: str) -> list[dict]:
    rows = []
    try:
        if ats == "ashby":
            for j in (kit.get_json(f"https://api.ashbyhq.com/posting-api/job-board/{org}") or {}).get("jobs", []):
                loc = j.get("location") or ""
                if j.get("isRemote"):
                    loc += " (Remote)"
                rows.append((j.get("title"), loc, j.get("jobUrl"), j.get("publishedAt")))
        elif ats == "greenhouse":
            for j in (kit.get_json(f"https://boards-api.greenhouse.io/v1/boards/{org}/jobs") or {}).get("jobs", []):
                rows.append((j.get("title"), (j.get("location") or {}).get("name", ""), j.get("absolute_url"),
                             j.get("first_published") or j.get("updated_at")))
        elif ats == "lever":
            for j in kit.get_json(f"https://api.lever.co/v0/postings/{org}?mode=json") or []:
                rows.append((j.get("text"), (j.get("categories") or {}).get("location", ""),
                             j.get("hostedUrl"), j.get("createdAt")))
        elif ats == "workable":
            by_url: dict = {}
            for j in (kit.get_json(f"https://apply.workable.com/api/v1/widget/accounts/{org}") or {}).get("jobs", []):
                r = by_url.setdefault(j.get("url"), [j.get("title"), [], j.get("url"), j.get("published_on"), False])
                r[1] += [", ".join(x for x in (l.get("city"), l.get("country")) if x) for l in j.get("locations") or []]
                r[4] |= bool(j.get("telecommuting"))
            for t, locs, u, d, remote in by_url.values():
                rows.append((t, "; ".join(dict.fromkeys(x for x in locs if x)) + (" (Remote)" if remote else ""), u, d))
        elif ats == "recruitee":
            for j in (kit.get_json(f"https://{org}.recruitee.com/api/offers/") or {}).get("offers", []):
                loc = ", ".join(x for x in (j.get("location"), j.get("country")) if x)
                rows.append((j.get("title"), loc + (" (Remote)" if j.get("remote") else ""),
                             j.get("careers_url"), j.get("published_at")))
    except Exception:
        return []
    return [{"company": org, "title": t or "", "location": l or "", "url": u or "",
             "age_days": kit.age_days(d), "source": f"ats:{ats}"} for t, l, u, d in rows if u]


def src_ats(_p) -> list[dict]:
    orgs = load_orgs()
    with ThreadPoolExecutor(12) as ex:
        return [r for rows in ex.map(lambda o: fetch_org(*o), orgs) for r in rows]


def src_jobicy(p) -> list[dict]:
    out = []
    for tag in (p.get("search", {}).get("board_tags") or ["product"]):
        for j in (kit.get_json(f"https://jobicy.com/api/v2/remote-jobs?count=100&tag={tag}") or {}).get("jobs", []):
            out.append({"company": j.get("companyName", ""), "title": j.get("jobTitle", ""),
                        "location": j.get("jobGeo", ""), "url": j.get("url", ""),
                        "age_days": kit.age_days(j.get("pubDate")), "source": "jobicy"})
    return out


def src_remoteok(p) -> list[dict]:
    out = []
    for tag in (p.get("search", {}).get("board_tags") or ["product"]):
        data = kit.get_json(f"https://remoteok.com/api?tag={tag}") or []
        for j in data[1:] if data and isinstance(data, list) else []:
            out.append({"company": (j.get("company") or "").strip(), "title": j.get("position", ""),
                        "location": j.get("location") or "", "url": j.get("url", ""),
                        "age_days": kit.age_days(j.get("date")), "source": "remoteok"})
    return out


def src_remotive(p) -> list[dict]:
    out = []
    for tag in (p.get("search", {}).get("board_tags") or ["product"]):
        data = kit.get_json(f"https://remotive.com/api/remote-jobs?search={tag}&limit=200") or {}
        for j in data.get("jobs", []):
            out.append({"company": (j.get("company_name") or "").strip(), "title": j.get("title", ""),
                        "location": j.get("candidate_required_location", ""), "url": j.get("url", ""),
                        "age_days": kit.age_days(j.get("publication_date")), "source": "remotive"})
    return out


SOURCES = {"ats": src_ats, "jobicy": src_jobicy, "remoteok": src_remoteok, "remotive": src_remotive}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--days", type=float)
    ap.add_argument("--only")
    ap.add_argument("--to-tracker", action="store_true")
    a = ap.parse_args()

    profile = kit.load_profile()
    gates = kit.Gates(profile)
    if a.days:
        gates.max_age = a.days
    names = [a.only] if a.only else (profile.get("search", {}).get("sources") or ["ats", "jobicy", "remoteok"])

    raw, stats = [], {}
    for n in names:
        if n not in SOURCES:
            print(f"  ! источник «{n}» неизвестен, есть: {', '.join(SOURCES)}")
            continue
        got = SOURCES[n](profile)
        stats[n] = len(got)
        raw += got

    seen = {} if a.all or not SEEN.exists() else json.loads(SEEN.read_text())
    rows_tracker = kit.tracker_rows()
    out, dropped = [], {"title": 0, "old": 0, "geo": 0, "company": 0, "seen": 0, "tracker": 0}
    uniq = {}
    for r in raw:
        uniq.setdefault(r["url"], r)
    for r in uniq.values():
        if not gates.title(r["title"]):
            dropped["title"] += 1
            continue
        if not gates.fresh(r["age_days"]):
            dropped["old"] += 1
            continue
        if not gates.company(r["company"]):
            dropped["company"] += 1
            continue
        r["geo"] = gates.geo(r["location"])
        if r["geo"] == "blocked":
            dropped["geo"] += 1
            continue
        if r["url"] in seen:
            dropped["seen"] += 1
            continue
        if kit.known(rows_tracker, r["company"], r["title"], r["url"]) == "dup":
            dropped["tracker"] += 1
            continue
        out.append(r)

    out.sort(key=lambda r: (r["geo"] != "wide", r["age_days"] if r["age_days"] is not None else 99))
    today = date.today().isoformat()
    for r in uniq.values():
        seen.setdefault(r["url"], today)
    kit.DATA.mkdir(exist_ok=True)
    SEEN.write_text(json.dumps(seen, ensure_ascii=False))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))

    print("Источники: " + ", ".join(f"{k} {v}" for k, v in stats.items()))
    print("Отсеяно: " + ", ".join(f"{k} {v}" for k, v in dropped.items() if v))
    print(f"\nНовых кандидатов: {len(out)}  (wide — гео подходит, check — открыть и прочитать)\n")
    for r in out:
        age = "?" if r["age_days"] is None else f"{r['age_days']:.0f}д"
        print(f"{r['geo']:<5} {age:>4}  {r['company'][:22]:<22} {r['title'][:60]:<60} {r['location'][:30]}")
        print(f"            {r['url']}")

    if a.to_tracker:
        import tracker
        rows = tracker.load()
        for r in out:
            if tracker.check(rows, r["company"], r["title"], r["url"])[0] != "dup":
                rid, n = tracker.slug(r["company"], r["title"]), 2
                while any(x["id"] == rid for x in rows):
                    rid, n = f"{tracker.slug(r['company'], r['title'])}-{n}", n + 1
                rows.append({"id": rid, "company": r["company"],
                             "role": r["title"], "url": r["url"], "source": r["source"],
                             "location": r["location"], "found_at": today,
                             "posted_days": r["age_days"] if r["age_days"] is not None else "",
                             "status": "found", "updated_at": today})
        tracker.save(rows)
        print(f"\nЗаписано в трекер: {len(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
