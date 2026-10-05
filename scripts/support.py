#!/usr/bin/env python3
"""Support ticket: bundle the problem + diagnostics, then send it the way the user chooses.

    jk support draft "<what happened>"     # writes data/support/<ts>.md, prints the path
    jk support send <file> private         # to the maintainer via telemetry channel (not public)
    jk support send <file> github          # prints a prefilled GitHub issue URL (public!)

Diagnostics added automatically: kit version, OS, Python, `jk setup --check` output, last 20
event names with errors (no CV text, no companies). The agent shows the draft to the user and
sends only after an explicit "send".
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA, FRAMEWORK, VERSION  # noqa: E402

DIR = DATA / "support"


def diagnostics() -> str:
    chk = subprocess.run([sys.executable, str(FRAMEWORK / "scripts" / "setup.py"), "--check"],
                         capture_output=True, text=True).stdout.strip()
    import events
    tail = [e.get("event") + (f":{e.get('kind') or e.get('name') or ''}") for e in events.read()[-20:]]
    return (f"- kit {VERSION} · {platform.system()} {platform.release()} · Python {platform.python_version()}\n"
            f"- setup check:\n```\n{chk}\n```\n- recent events: {', '.join(tail) or 'none'}")


def draft(text: str) -> Path:
    DIR.mkdir(parents=True, exist_ok=True)
    p = DIR / f"{datetime.now():%Y%m%d-%H%M%S}.md"
    p.write_text(f"## Problem\n{text}\n\n## Diagnostics\n{diagnostics()}\n", encoding="utf-8")
    return p


def send(p: Path, how: str) -> int:
    body = p.read_text(encoding="utf-8")
    title = body.split("\n", 2)[1][:80] if "\n" in body else "Support"
    if how == "github":
        repo = json.loads((FRAMEWORK / "config" / "telemetry.json").read_text()).get("issues_repo")
        if not repo:
            print("no issues_repo in config/telemetry.json — use: private")
            return 1
        q = urllib.parse.urlencode({"title": title, "body": body, "labels": "support"})
        print(f"https://github.com/{repo}/issues/new?{q}")
        print("Public page: check the text has no personal data before pressing Submit.")
        return 0
    import telemetry
    ok = telemetry.send("support_ticket", {"title": title, "body": body[:8000]})
    print("sent to maintainer" if ok else "queued — will be sent when online / when the endpoint is set")
    return 0


def main() -> int:
    a = sys.argv[1:]
    if a[:1] == ["draft"] and len(a) > 1:
        print(draft(" ".join(a[1:])))
        return 0
    if a[:1] == ["send"] and len(a) == 3:
        return send(Path(a[1]), a[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
