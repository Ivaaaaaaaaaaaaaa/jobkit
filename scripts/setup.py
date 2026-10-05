#!/usr/bin/env python3
"""One-shot, idempotent setup. Safe to re-run any time (also after a plugin update).

    jk setup            # check & fix everything machine-side, print what's left for the agent
    jk setup --check    # only report, change nothing (this is also `jk doctor`)

Machine-side steps (this script):
  1. python   — 3.10+
  2. venv     — ~/.jobkit/venv with pyyaml, python-docx, pypdf (shared by all projects, survives updates)
  3. pdf      — LibreOffice for PDF CVs (optional; prints the install command)
  4. folders  — me/, data/ from templates (never overwrites), .gitignore for me/ and data/
  5. perms    — .claude/settings.json in this folder: allow `jk` so the agent doesn't ask every time
  6. ping     — anonymous install event (telemetry.py), opt-out respected
Agent-side steps (/setup command): Chrome extension, CV + LinkedIn import, profile questions,
boards fit, first scan. Output is compact on purpose: the agent reads it.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import venv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA, FRAMEWORK, HOME, ME, VERSION  # noqa: E402

VENV = Path.home() / ".jobkit" / "venv"
VPY = VENV / "bin" / "python"
DEPS = ["pyyaml", "python-docx", "pypdf"]
CHECK = "--check" in sys.argv
results: dict[str, str] = {}


def step(name: str, ok: bool, note: str = "") -> bool:
    results[name] = ("ok" if ok else "FAIL") + (f" — {note}" if note else "")
    return ok


def has_deps(py: Path | str) -> bool:
    r = subprocess.run([str(py), "-c", "import yaml, docx, pypdf"], capture_output=True)
    return r.returncode == 0


def main() -> int:
    first = not (ME / "profile.yaml").exists()
    step("python", sys.version_info >= (3, 10), platform_py())

    if VPY.exists() and has_deps(VPY):
        step("venv", True, str(VENV))
    elif CHECK:
        step("venv", False, "run: jk setup")
    else:
        try:
            if not VPY.exists():
                venv.create(VENV, with_pip=True)
            r = subprocess.run([str(VPY), "-m", "pip", "install", "-q", "--disable-pip-version-check", *DEPS],
                               capture_output=True, text=True)
            step("venv", r.returncode == 0 and has_deps(VPY),
                 str(VENV) if r.returncode == 0 else r.stderr.strip().splitlines()[-1][:160])
        except Exception as e:  # noqa: BLE001
            step("venv", False, f"{e}; fallback: python3 -m pip install --user {' '.join(DEPS)}")

    soffice = shutil.which("soffice") or Path("/Applications/LibreOffice.app").exists()
    results["pdf"] = "ok" if soffice else "skip — optional: brew install --cask libreoffice (DOCX works without it)"

    if not CHECK:
        for d in (ME / "cv", DATA / "applications"):
            d.mkdir(parents=True, exist_ok=True)
        for src in (FRAMEWORK / "templates").rglob("*"):
            if src.is_file():
                dst = ME / src.relative_to(FRAMEWORK / "templates")
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        gi = HOME / ".gitignore"
        lines = gi.read_text().splitlines() if gi.exists() else []
        add = [x for x in ("me/", "data/") if x not in lines]
        if add:
            gi.write_text("\n".join(lines + ["# job search: personal data", *add]) + "\n")
    todo = sum(p.read_text(encoding="utf-8").count("TODO") for p in ME.rglob("*") if p.is_file()) if ME.exists() else -1
    step("folders", ME.exists() and DATA.exists(), f"{HOME} · TODO left in me/: {todo}")

    jk = FRAMEWORK / "scripts" / "jk.py"
    rule = f"Bash(python3 {jk}:*)"
    sp = HOME / ".claude" / "settings.json"
    try:
        cfg = json.loads(sp.read_text()) if sp.exists() else {}
    except ValueError:
        cfg = {}
    allow = cfg.setdefault("permissions", {}).setdefault("allow", [])
    stale = [r for r in allow if r.startswith("Bash(python3 ") and r.endswith("/scripts/jk.py:*)") and r != rule]
    if rule in allow and not stale:
        step("perms", True)
    elif CHECK:
        step("perms", False, "run: jk setup")
    else:
        cfg["permissions"]["allow"] = [r for r in allow if r not in stale] + ([rule] if rule not in allow else [])
        sp.parent.mkdir(exist_ok=True)
        sp.write_text(json.dumps(cfg, indent=2) + "\n")
        step("perms", True, "updated after plugin move/update" if stale else "added")

    if not CHECK:
        try:
            import telemetry
            sent = telemetry.send("install", {"first": first, "steps_ok": sum(v.startswith("ok") for v in results.values()),
                                              "steps_failed": [k for k, v in results.items() if v.startswith("FAIL")]})
            step("telemetry", True, ("on" if telemetry.enabled() else "off") + (", sent" if sent else ", queued"))
        except Exception as e:  # noqa: BLE001
            step("telemetry", True, f"skipped: {e}")

    print(f"jobkit {VERSION} setup{' check' if CHECK else ''}")
    for k, v in results.items():
        print(f"  {k:<9} {v}")
    hard = [k for k, v in results.items() if v.startswith("FAIL")]
    print("next: agent steps (chrome, import CV/LinkedIn, profile, boards fit)" if not hard
          else f"fix first: {', '.join(hard)}")
    return 1 if hard else 0


def platform_py() -> str:
    return f"{sys.version.split()[0]} at {sys.executable}"


if __name__ == "__main__":
    sys.exit(main())
