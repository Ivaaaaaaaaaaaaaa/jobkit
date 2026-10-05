#!/usr/bin/env python3
"""Usage and outcome metrics, computed locally from data/tracker.csv + data/events.jsonl.

    python3 scripts/metrics.py            # report for the user
    python3 scripts/metrics.py --share    # anonymized aggregate -> data/metrics-share.json
                                          # (no companies, roles, links or texts — counts only)

What it answers:
  outcome  — funnel found -> applied -> response -> interview -> offer, response rate,
             days to first response, applications per week;
  what works — response rate by track, source and score band (shown when n >= 5);
  where leads die — gate reasons for skipped roles;
  usage    — active days, commands used, scans and their yield, CVs built, audit pass rate.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import events  # noqa: E402
import tracker  # noqa: E402
from paths import DATA, VERSION  # noqa: E402

RESPONDED = {"screening", "interview", "test", "final", "offer"}
INTERVIEW = {"interview", "test", "final", "offer"}
REACHED_APPLY = RESPONDED | {"applied", "rejected", "withdrawn"}
MIN_N = 5


def band(score: str) -> str:
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "none"
    return "high" if s >= 8 else "medium" if s >= 5 else "low"


def rate(num: int, den: int) -> float | None:
    return round(num / den, 3) if den else None


def compute() -> dict:
    rows, ev = tracker.load(), events.read()
    applied = [r for r in rows if r["status"] in REACHED_APPLY and (r.get("applied_at") or r["status"] != "rejected")]
    responded = [r for r in applied if r["status"] in RESPONDED
                 or (r["status"] == "rejected" and r.get("applied_at"))]  # a rejection is a response too
    by_status = Counter(r["status"] for r in rows)

    def breakdown(key) -> dict:
        groups = defaultdict(lambda: [0, 0])
        for r in applied:
            g = groups[key(r) or "none"]
            g[0] += 1
            g[1] += r["status"] in RESPONDED
        return {k: {"applied": a, "responded": b, "rate": rate(b, a)} for k, (a, b) in groups.items() if a >= MIN_N}

    first_resp = [e["days_since_applied"] for e in ev if e.get("event") == "status" and e.get("frm") == "applied"
                  and e.get("to") in RESPONDED | {"rejected"} and isinstance(e.get("days_since_applied"), int)]

    weeks = Counter()
    for r in applied:
        if r.get("applied_at"):
            d = datetime.fromisoformat(r["applied_at"]).date()
            weeks[(d - timedelta(days=d.weekday())).isoformat()] += 1

    reasons = Counter()
    for r in rows:
        if r["status"] == "skipped":
            m = re.search(r"(гейт|gate)\s*(\d+)", r.get("comment", ""), re.I)
            reasons[f"gate {m.group(2)}" if m else "other"] += 1

    scans = [e for e in ev if e.get("event") == "scan"]
    audits = [e for e in ev if e.get("event") == "audit"]
    days = sorted({e["ts"][:10] for e in ev if e.get("ts")})
    today = date.today().isoformat()
    return {
        "version": VERSION,
        "generated": today,
        "outcome": {
            "leads": len(rows),
            "by_status": dict(by_status),
            "applied": len(applied),
            "responded": len(responded),
            "interviews": sum(r["status"] in INTERVIEW for r in rows),
            "offers": by_status.get("offer", 0),
            "response_rate": rate(len(responded), len(applied)),
            "interview_rate": rate(sum(r["status"] in INTERVIEW for r in applied), len(applied)),
            "median_days_to_response": statistics.median(first_resp) if first_resp else None,
            "applications_per_week": dict(sorted(weeks.items())[-6:]),
        },
        "what_works": {
            "by_track": breakdown(lambda r: r.get("track")),
            "by_source": breakdown(lambda r: (r.get("source") or "").split(":")[0]),
            "by_score_band": breakdown(lambda r: band(r.get("score"))),
        },
        "skipped_reasons": dict(reasons.most_common()),
        "usage": {
            "first_day": days[0] if days else None,
            "last_day": days[-1] if days else None,
            "active_days": len(days),
            "commands": dict(Counter(e.get("name") for e in ev if e.get("event") == "command").most_common()),
            "scans": len(scans),
            "avg_new_per_scan": round(statistics.mean(s.get("new", 0) for s in scans), 1) if scans else None,
            "cv_built": dict(Counter(e.get("kind") for e in ev if e.get("event") == "cv_render")),
            "audits": len(audits),
            "audit_pass_rate": rate(sum(bool(a.get("ok")) for a in audits), len(audits)),
            "audit_problems": dict(Counter(p for a in audits for p in a.get("problems", [])).most_common(5)),
        },
        "health": {
            "last_scan": scans[-1]["ts"][:10] if scans else None,
            "found_older_than_14d": sum(1 for r in rows if r["status"] == "found" and r.get("found_at")
                                        and (date.today() - date.fromisoformat(r["found_at"])).days > 14),
            "overdue_next_steps": sum(1 for r in rows if r.get("next_date") and r["next_date"] < today
                                      and r["status"] not in {"rejected", "withdrawn", "skipped", "offer"}),
        },
    }


def pct(x) -> str:
    return "—" if x is None else f"{x:.0%}"


def report(m: dict) -> None:
    o, u, h = m["outcome"], m["usage"], m["health"]
    print(f"Leads {o['leads']} · applied {o['applied']} · responses {o['responded']} ({pct(o['response_rate'])})"
          f" · interviews {o['interviews']} ({pct(o['interview_rate'])}) · offers {o['offers']}")
    if o["median_days_to_response"] is not None:
        print(f"Median days to first response: {o['median_days_to_response']}")
    if o["applications_per_week"]:
        print("Applications per week: " + ", ".join(f"{k[5:]}: {v}" for k, v in o["applications_per_week"].items()))
    for name, data in m["what_works"].items():
        if data:
            print(f"Response rate {name.replace('by_', 'by ')}: "
                  + ", ".join(f"{k} {pct(v['rate'])} (n={v['applied']})" for k, v in data.items()))
    if not any(m["what_works"].values()):
        print(f"What works: not enough data yet (need {MIN_N}+ applications per group).")
    if m["skipped_reasons"]:
        print("Skipped by: " + ", ".join(f"{k} {v}" for k, v in m["skipped_reasons"].items()))
    print(f"Usage: {u['active_days']} active days, scans {u['scans']} (avg new {u['avg_new_per_scan']}), "
          f"CVs {sum(u['cv_built'].values())}, audit pass {pct(u['audit_pass_rate'])}")
    if u["commands"]:
        print("Commands: " + ", ".join(f"/{k} {v}" for k, v in u["commands"].items()))
    flags = []
    if h["last_scan"] and (date.today() - date.fromisoformat(h["last_scan"])).days > 3:
        flags.append(f"last scan {h['last_scan']} — run /find")
    if h["found_older_than_14d"]:
        flags.append(f"{h['found_older_than_14d']} leads stuck in found >14d — apply or skip")
    if h["overdue_next_steps"]:
        flags.append(f"{h['overdue_next_steps']} overdue next steps — /status")
    if flags:
        print("Attention: " + "; ".join(flags))


def main() -> int:
    m = compute()
    if "--share" in sys.argv:
        out = DATA / "metrics-share.json"
        out.write_text(json.dumps(m, ensure_ascii=False, indent=1))
        print(f"Anonymized metrics: {out}\nNo companies, roles, links or texts inside — safe to send.")
    elif "--json" in sys.argv:
        print(json.dumps(m, ensure_ascii=False, indent=1))
    else:
        report(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
