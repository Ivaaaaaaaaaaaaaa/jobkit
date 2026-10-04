#!/usr/bin/env python3
"""Трекер откликов: один CSV-файл — единственный источник правды о каждой вакансии.

Зачем CSV, а не база: открывается в Excel/Numbers/Google Sheets, не требует ключей,
переносится копированием папки. Если захочешь Notion или Google Sheets — см.
playbooks/data-storage.md: колонки те же, меняется только место хранения.

Команды:
    python scripts/tracker.py add  --company X --role Y --url URL [--source S] [--location L]
                                   [--posted-days N] [--score N] [--track T] [--status found]
                                   [--comment "..."]
    python scripts/tracker.py check "Компания::Роль" URL ["Компания2::Роль2" URL2 ...]
    python scripts/tracker.py set  <id|url> <статус> ["комментарий"] [--next "что" --date YYYY-MM-DD]
    python scripts/tracker.py list [--status applied] [--company X]
    python scripts/tracker.py funnel
    python scripts/tracker.py due            # что пора сделать сегодня (follow-up, тестовые)
    python scripts/tracker.py --selftest

Дедуп (`check`) печатает:
    ⛔  та же роль у той же компании или та же ссылка  -> не подаваться (exit 1)
    ⚠   та же компания, другая роль                    -> прочитать список глазами
    ✅  нового нет в трекере
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "data" / "tracker.csv"

COLUMNS = ["id", "company", "role", "url", "source", "location", "found_at", "posted_days",
           "score", "track", "status", "applied_at", "next_action", "next_date", "cv_path",
           "comment", "updated_at"]

# Статус движется вперёд; rejected / withdrawn / skipped — конечные.
STATUSES = ["found", "ready", "applied", "screening", "interview", "test", "final", "offer",
            "rejected", "withdrawn", "skipped"]
ACTIVE = {"applied", "screening", "interview", "test", "final"}

LEGAL = r"\b(inc|ltd|llc|gmbh|bv|ag|sa|sas|plc|limited|corp|corporation|co|group|technologies|labs?)\b"


def norm_company(s: str) -> str:
    s = re.sub(LEGAL, " ", (s or "").lower())
    return re.sub(r"[^a-z0-9а-яё]+", "", s)          # «Fundraise Up» == «FundraiseUp»


def norm_role(s: str) -> str:
    s = re.sub(r"\(.*?\)", " ", (s or "").lower())    # «PM (AI)» == «PM»
    s = re.sub(r"\b(sr|snr)\b", "senior", s)
    return re.sub(r"[^a-z0-9а-яё]+", " ", s).strip()


def norm_url(u: str) -> str:
    """Одна вакансия в разных написаниях ссылки -> один ключ."""
    if not u:
        return ""
    p = urlparse(u.strip())
    q = parse_qs(p.query)
    for key in ("gh_jid", "jobId", "job_id", "jk", "currentJobId"):   # id вакансии в query
        if key in q:
            return f"{key}={q[key][0]}"
    path = re.sub(r"/(apply|application|applications?/new)/?$", "", p.path.rstrip("/"))
    host = p.netloc.lower().replace("www.", "").replace("job-boards.", "boards.")
    return f"{host}{path}".lower()


def load() -> list[dict]:
    if not TRACKER.exists():
        return []
    with TRACKER.open(encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def save(rows: list[dict]) -> None:
    TRACKER.parent.mkdir(parents=True, exist_ok=True)
    tmp = TRACKER.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})
    tmp.replace(TRACKER)


def slug(company: str, role: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", f"{company}-{role}".lower()).strip("-")[:60]


def find(rows: list[dict], key: str) -> dict | None:
    for r in rows:
        if r["id"] == key or (key.startswith("http") and norm_url(r["url"]) == norm_url(key)):
            return r
    return None


def check(rows: list[dict], company: str, role: str, url: str) -> tuple[str, list[dict]]:
    nc, nr, nu = norm_company(company), norm_role(role), norm_url(url)
    same_url = [r for r in rows if nu and norm_url(r["url"]) == nu]
    same_co = [r for r in rows if nc and norm_company(r["company"]) == nc]
    same_role = [r for r in same_co if nr and norm_role(r["role"]) == nr]
    if same_url or same_role:
        return "dup", same_url or same_role
    if same_co:
        return "company", same_co
    return "new", []


def cmd_add(a) -> int:
    rows = load()
    verdict, hits = check(rows, a.company, a.role, a.url)
    if verdict == "dup":
        print(f"⛔ уже в трекере: {hits[0]['id']} [{hits[0]['status']}]")
        return 1
    today = date.today().isoformat()
    base, n, rid = slug(a.company, a.role), 2, slug(a.company, a.role)
    while any(r["id"] == rid for r in rows):
        rid, n = f"{base}-{n}", n + 1
    rows.append({"id": rid, "company": a.company, "role": a.role, "url": a.url,
                 "source": a.source or "", "location": a.location or "", "found_at": today,
                 "posted_days": a.posted_days or "", "score": a.score or "", "track": a.track or "",
                 "status": a.status, "comment": a.comment or "", "updated_at": today})
    save(rows)
    note = "  (⚠ компания уже есть с другой ролью)" if verdict == "company" else ""
    print(f"✅ добавлено: {rid}{note}")
    return 0


def cmd_check(a) -> int:
    rows, args, worst = load(), a.items, 0
    i = 0
    while i < len(args):
        pair = args[i]
        url = args[i + 1] if i + 1 < len(args) and args[i + 1].startswith("http") else ""
        i += 2 if url else 1
        company, _, role = pair.partition("::")
        if not role:
            print(f"⚠ «{pair}»: без ::Роль проверяется только компания — для решения о подаче мало")
        verdict, hits = check(rows, company, role, url)
        if verdict == "dup":
            worst = 1
            print(f"⛔ {pair}: уже есть — " + "; ".join(f"{h['id']} [{h['status']}]" for h in hits))
        elif verdict == "company":
            print(f"⚠ {pair}: компания есть, роль ДРУГАЯ. Ранее: "
                  + "; ".join(f"{h['role']} [{h['status']}]" for h in hits))
        else:
            print(f"✅ {pair}: нового нет в трекере")
    return worst


def cmd_set(a) -> int:
    if a.status not in STATUSES:
        print(f"Статус «{a.status}» не из списка: {', '.join(STATUSES)}")
        return 2
    rows = load()
    r = find(rows, a.key)
    if not r:
        print(f"Не нашёл «{a.key}». Сперва add.")
        return 1
    today = date.today().isoformat()
    r["status"], r["updated_at"] = a.status, today
    if a.status == "applied" and not r.get("applied_at"):
        r["applied_at"] = today
    if a.comment:
        r["comment"] = (r.get("comment", "") + f" | {today}: {a.comment}").strip(" |")
    if a.next:
        r["next_action"], r["next_date"] = a.next, a.date or ""
    save(rows)
    print(f"✅ {r['id']} -> {a.status}")
    return 0


def cmd_list(a) -> int:
    rows = load()
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    if a.company:
        rows = [r for r in rows if norm_company(a.company) in norm_company(r["company"])]
    for r in rows:
        print(f"{r['status']:<10} {r['score'] or '-':>3}  {r['company']} — {r['role']}  {r['url']}")
    print(f"\nвсего: {len(rows)}")
    return 0


def cmd_funnel(_a) -> int:
    rows = load()
    by = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    applied = sum(by[s] for s in STATUSES[2:])  # всё, что дошло до подачи и дальше
    print(f"Всего вакансий: {len(rows)}")
    for s in STATUSES:
        if by[s]:
            print(f"  {s:<10} {by[s]}")
    reached = applied - by["applied"] - by["withdrawn"] - by["skipped"]
    if applied:
        print(f"\nКонверсия подача -> любой ответ компании: {reached}/{applied} = {reached / applied:.0%}")
    return 0


def cmd_due(_a) -> int:
    today = date.today().isoformat()
    rows = [r for r in load() if r.get("next_date") and r["next_date"] <= today]
    for r in rows:
        print(f"{r['next_date']}  {r['company']} — {r['role']}: {r['next_action']}")
    stale = [r for r in load() if r["status"] == "applied" and r.get("applied_at")
             and (date.today() - datetime.fromisoformat(r["applied_at"]).date()).days >= 7
             and not r.get("next_action")]
    for r in stale:
        print(f"тишина 7+ дней: {r['company']} — {r['role']} (подано {r['applied_at']}) -> follow-up?")
    if not rows and not stale:
        print("На сегодня дел нет.")
    return 0


def selftest() -> int:
    assert norm_company("Fundraise Up Inc.") == norm_company("FundraiseUp")
    assert norm_role("Sr. Product Manager (AI)") == norm_role("Senior Product Manager")
    assert norm_url("https://job-boards.greenhouse.io/acme/jobs/123?utm=x") == \
        norm_url("https://boards.greenhouse.io/acme/jobs/123/")
    assert norm_url("https://acme.com/careers?gh_jid=555") == norm_url("https://x.io/a?gh_jid=555")
    assert norm_url("https://jobs.ashbyhq.com/acme/uuid/application") == \
        norm_url("https://jobs.ashbyhq.com/acme/uuid")
    rows = [{"id": "a", "company": "Acme", "role": "Product Manager", "url": "https://x.io/1",
             "status": "applied"}]
    assert check(rows, "ACME Ltd", "Product Manager", "")[0] == "dup"
    assert check(rows, "Acme", "Growth PM", "")[0] == "company"
    assert check(rows, "Other", "PM", "https://x.io/1/")[0] == "dup"
    assert check(rows, "Other", "PM", "")[0] == "new"
    print("tracker selftest: ok")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("--company", required=True)
    s.add_argument("--role", required=True)
    s.add_argument("--url", default="")
    s.add_argument("--source")
    s.add_argument("--location")
    s.add_argument("--posted-days", dest="posted_days")
    s.add_argument("--score")
    s.add_argument("--track")
    s.add_argument("--status", default="found", choices=STATUSES)
    s.add_argument("--comment")
    s = sub.add_parser("check")
    s.add_argument("items", nargs="+")
    s = sub.add_parser("set")
    s.add_argument("key")
    s.add_argument("status")
    s.add_argument("comment", nargs="?")
    s.add_argument("--next")
    s.add_argument("--date")
    s = sub.add_parser("list")
    s.add_argument("--status")
    s.add_argument("--company")
    sub.add_parser("funnel")
    sub.add_parser("due")
    a = p.parse_args()
    return {"add": cmd_add, "check": cmd_check, "set": cmd_set, "list": cmd_list,
            "funnel": cmd_funnel, "due": cmd_due}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
