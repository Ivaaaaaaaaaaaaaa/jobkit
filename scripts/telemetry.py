"""Anonymous telemetry: install pings, monthly aggregates, private support tickets.

What is sent (and nothing else):
  install         — kit version, OS, Python version, first install or re-run, setup steps passed
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
import platform
import sys
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
    import os
    if os.environ.get("JK_TELEMETRY_OFF") or _state().get("enabled") is False:
        return False
    try:
        import yaml
        p = yaml.safe_load((ME / "profile.yaml").read_text()) or {}
        if p.get("telemetry") is False:
            return False
    except Exception:
        pass
    return True


def install_id() -> str:
    s = _state()
    if not s.get("id"):
        s["id"] = str(uuid.uuid4())
        s.setdefault("enabled", True)
        _save_state(s)
    return s["id"]


def _post(batch: list[dict]) -> bool:
    cfg = _config()
    if not cfg.get("key") or not cfg.get("host"):
        return False
    body = json.dumps({"api_key": cfg["key"], "batch": batch}).encode()
    try:
        req = urllib.request.Request(cfg["host"].rstrip("/") + "/batch/", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def send(event: str, props: dict | None = None) -> bool:
    """Queue the event and try to flush the queue. Returns True if delivered now."""
    if not enabled() or not DATA.exists():
        return False
    rec = {"event": event, "distinct_id": install_id(),
           "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "properties": {"kit_version": VERSION, "os": platform.system(),
                          "python": platform.python_version(), "$process_person_profile": False,
                          **(props or {})}}
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return flush()


def flush() -> bool:
    if not OUTBOX.exists():
        return True
    lines = [json.loads(l) for l in OUTBOX.read_text(encoding="utf-8").splitlines() if l.strip()]
    if lines and _post(lines):
        OUTBOX.unlink()
        return True
    return False


def monthly_tick() -> None:
    """Once per calendar month send a cumulative metrics snapshot. Called from the prompt hook — cheap."""
    if not enabled() or not (ME / "profile.yaml").exists():
        return
    s = _state()
    month = date.today().strftime("%Y-%m")
    if s.get("last_monthly") == month:
        return
    s["last_monthly"] = month
    _save_state(s)
    try:
        import metrics
        m = metrics.compute()
        send("monthly_stats", {"month": month, "outcome": m["outcome"], "what_works": m["what_works"],
                               "skipped_reasons": m["skipped_reasons"], "usage": m["usage"], "health": m["health"]})
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
