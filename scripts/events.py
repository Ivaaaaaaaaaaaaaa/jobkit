"""Local usage log: data/events.jsonl, one JSON per line. Nothing leaves the machine.

Scripts call `log("event", **props)`. Props are counts, enums and ids — never CV text,
answers or letters. Company/role are kept locally for the user's own report; the shareable
export (`metrics.py --share`) drops them.

Hook mode — records which slash command was used (name only, never the prompt text):
    python3 scripts/events.py hook   < UserPromptSubmit JSON on stdin
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA, ME, VERSION  # noqa: E402

LOG = DATA / "events.jsonl"
COMMANDS = {"setup", "cv-interview", "positioning", "find", "apply", "jobs-run", "cv", "pipeline",
            "interview-prep", "support", "stats"}


def log(event: str, **props) -> None:
    try:
        if not (ME / "profile.yaml").exists():
            return  # not a job-search folder (the plugin hook runs in every project)
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "v": VERSION, "event": event}
        rec.update({k: v for k, v in props.items() if v not in (None, "")})
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # analytics must never break the real work


def read() -> list[dict]:
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def hook() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not (ME / "profile.yaml").exists():
        return 0
    m = re.match(r"\s*/([\w:-]+)", payload.get("prompt") or "")
    if m and (m.group(1).startswith("jobkit:") or m.group(1) in COMMANDS):
        log("command", name=m.group(1).split(":")[-1])
    try:
        import telemetry
        telemetry.monthly_tick()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(hook() if sys.argv[1:2] == ["hook"] else 0)
