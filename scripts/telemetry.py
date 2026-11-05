"""Anonymous telemetry: install pings, monthly aggregates, private support tickets.

What is sent (and nothing else):
  install         — kit version, OS, Python version and kind (stock/brew/other), first install or
                    re-run, setup steps passed/failed
  onboarding_step — a setup phase done / skipped / failed (+ a short failure code), minutes since start
  onboarding_done — all phases finished, minutes it took, which were skipped
  daily_active    — once per active day: days since install, commands used since the last ping,
                    totals (leads, applied, responses, interviews, offers) — counts only
  milestone       — once each: first_scan, first_lead, first_cv, first_application, first_response,
                    first_interview, first_offer
  crash           — a jk script died: script name, exception type, function and line (no message)
  monthly_stats   — once a month, a cumulative snapshot from metrics.py: counts and rates only
                    (no companies, roles, links, CV or letter text, no contacts)
  support_ticket  — only when the user writes one and confirms sending; their text as written

Identity: a random install id (data/telemetry.json). No name, email or IP-derived location
is attached by the kit. Opt out: `jk telemetry off` or profile.yaml -> telemetry: false.

Transport: PostHog batch API (config/telemetry.json, US cloud). Its project key is public by design —
it can only write events, not read them. Empty key = events wait in data/telemetry-outbox.jsonl
and go out after an update brings a key. Network errors never break the user's work.
"""
from __future__ import annotations

import json
import os
import platform
import re
import sys
import time
import urllib.request
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA, FRAMEWORK, ME, VERSION  # noqa: E402

STATE = DATA / "telemetry.json"
OUTBOX = DATA / "telemetry-outbox.jsonl"
CONFIG = FRAMEWORK / "config" / "telemetry.json"


def _config() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except Exception:
        return {}


def _state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def _save_state(s: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1))


def enabled() -> bool:
    if os.environ.get("JK_TELEMETRY_OFF") or _state().get("enabled") is False:
        return False
    try:
        text = (ME / "profile.yaml").read_text(encoding="utf-8")
    except Exception:
        return True
    # The prompt hook runs on bare python3 without PyYAML: read the switch with a regex as well.
    if re.search(r"^telemetry:\s*(false|no|off)\b", text, re.M | re.I):
        return False
    try:
        import yaml
        if (yaml.safe_load(text) or {}).get("telemetry") is False:
            return False
    except Exception:
        pass
    return True


def install_id() -> str:
    s = _state()
    if not s.get("id"):
        s["id"] = str(uuid.uuid4())
        s.setdefault("enabled", True)
        s.setdefault("first_seen", date.today().isoformat())
        _save_state(s)
    return s["id"]


def py_kind() -> str:
    exe = sys.base_prefix + " " + sys.executable
    if "CommandLineTools" in exe or exe.startswith("/System/") or "/Applications/Xcode" in exe:
        return "stock"
    if "homebrew" in exe or "/usr/local/Cellar" in exe:
        return "brew"
    return "uv" if "/uv/" in exe else "other"


def code(text: str, n: int = 40) -> str:
    """A short machine code from free text: lowercase, [a-z0-9_-] only — never a sentence."""
    return re.sub(r"[^a-z0-9_-]+", "_", (text or "").lower()).strip("_")[:n]


def _post(batch: list[dict]) -> bool:
    cfg = _config()
    if not cfg.get("key") or not cfg.get("host"):
        return False
    body = json.dumps({"api_key": cfg["key"], "batch": batch}).encode()
    try:
        req = urllib.request.Request(cfg["host"].rstrip("/") + "/batch/", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def queue(event: str, props: dict | None = None) -> bool:
    """Append the event to the outbox without sending. False when telemetry is off."""
    if not enabled() or not DATA.exists():
        return False
    rec = {"event": event, "distinct_id": install_id(),
           "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
           "properties": {"kit_version": VERSION, "os": platform.system(),
                          "python": platform.python_version(), "$process_person_profile": False,
                          **({"is_test": True} if os.environ.get("JK_TELEMETRY_TEST") else {}),
                          **(props or {})}}
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return True


def send(event: str, props: dict | None = None) -> bool:
    """Queue the event and try to flush the queue. Returns True if delivered now."""
    return queue(event, props) and flush()


def flush() -> bool:
    if not OUTBOX.exists():
        return True
    lines = [json.loads(l) for l in OUTBOX.read_text(encoding="utf-8").splitlines() if l.strip()]
    if lines and _post(lines):
        OUTBOX.unlink()
        return True
    return False


MILESTONES = [
    ("first_scan", lambda m: m["usage"]["scans"] > 0),
    ("first_lead", lambda m: m["outcome"]["leads"] > 0),
    ("first_cv", lambda m: sum(m["usage"]["cv_built"].values()) > 0),
    ("first_application", lambda m: m["outcome"]["applied"] > 0),
    ("first_response", lambda m: m["outcome"]["responded"] > 0),
    ("first_interview", lambda m: m["outcome"]["interviews"] > 0),
    ("first_offer", lambda m: m["outcome"]["offers"] > 0),
]
CHECK_EVERY = 600  # seconds between milestone checks: the hook runs on every prompt


def totals(m: dict) -> dict:
    o = m["outcome"]
    return {"leads": o["leads"], "applied": o["applied"], "responded": o["responded"],
            "interviews": o["interviews"], "offers": o["offers"]}


def tick() -> None:
    """Called from the prompt hook. Cheap when nothing is due: one state read, no metrics."""
    if not enabled() or not (ME / "profile.yaml").exists():
        return
    s = _state()
    today, month, now = date.today().isoformat(), date.today().strftime("%Y-%m"), time.time()
    pending = [n for n, _ in MILESTONES if n not in s.get("milestones", [])]
    due_daily, due_monthly = s.get("last_daily") != today, s.get("last_monthly") != month
    due_check = pending and now - s.get("last_check", 0) > CHECK_EVERY
    if not (due_daily or due_monthly or due_check):
        return
    try:
        import events
        import metrics
        m = metrics.compute()
    except Exception:
        return
    install_id()
    s = _state()
    s.setdefault("first_seen", today)   # installs from 0.2.0 had no first_seen
    s["last_check"] = now
    hits = [n for n, ok in MILESTONES if n in pending and ok(m)]
    s["milestones"] = s.get("milestones", []) + hits
    since = s.get("last_daily_ts", "")
    prev_daily, prev_monthly = s.get("last_daily"), s.get("last_monthly")
    if due_daily:
        s["last_daily"], s["last_daily_ts"] = today, datetime.now(timezone.utc).isoformat(timespec="seconds")
    if due_monthly:
        s["last_monthly"] = month
    for n in hits:
        queue("milestone", {"name": n})
    if due_daily:
        cmds = {}
        for e in events.read():
            if e.get("event") == "command" and e.get("ts", "") > since:
                cmds[e.get("name")] = cmds.get(e.get("name"), 0) + 1
        first = s.get("first_seen") or today
        queue("daily_active", {"days_since_install": (date.today() - date.fromisoformat(first)).days,
                              "days_since_last_active": (date.today() - date.fromisoformat(prev_daily)).days
                              if prev_daily else None,
                              "commands": cmds, "totals": totals(m), "active_days": m["usage"]["active_days"]})
    if due_monthly and prev_monthly != month:
        queue("monthly_stats", {"month": month, "outcome": m["outcome"], "what_works": m["what_works"],
                                "skipped_reasons": m["skipped_reasons"], "usage": m["usage"], "health": m["health"]})
    _save_state(s)   # events are already in the outbox: a killed hook loses nothing
    flush()          # one POST for the whole batch


def monthly_tick() -> None:  # kept for older hooks
    tick()


def report_crash(script: str, exc: BaseException) -> None:
    """A jk script died. Sends the exception type and where — never the message (may hold data)."""
    try:
        tb = exc.__traceback__
        while tb and tb.tb_next:
            tb = tb.tb_next
        where = f"{Path(tb.tb_frame.f_code.co_filename).name}:{tb.tb_frame.f_code.co_name}:{tb.tb_lineno}" if tb else ""
        send("crash", {"script": re.sub(r"[^a-z0-9_.-]+", "_", (script or "").lower())[:40], "error": type(exc).__name__, "where": where})
    except Exception:
        pass


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    s = _state()
    if arg in ("on", "off"):
        s["enabled"] = arg == "on"
        _save_state(s)
        print(f"telemetry {arg}")
    elif arg == "flush":
        print("sent" if flush() else "queued (no key or offline)")
    else:
        cfg = _config()
        q = len(OUTBOX.read_text().splitlines()) if OUTBOX.exists() else 0
        print(f"telemetry: {'on' if enabled() else 'off'} · id {s.get('id', '-')[:8]} · "
              f"endpoint {'set' if cfg.get('key') else 'not set'} · queued {q} · last monthly {s.get('last_monthly', '-')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
