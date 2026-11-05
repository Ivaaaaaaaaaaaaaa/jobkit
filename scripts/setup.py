#!/usr/bin/env python3
"""One-shot, idempotent setup. Safe to re-run any time (also after a plugin update).

    jk setup            # check & fix everything machine-side, print what's left for the agent
    jk setup --check    # only report, change nothing (this is also `jk doctor`)
    jk setup --phase <name> [--skip | --fail <code>]   # agent marks an onboarding phase
                        # names: machine browser import profile boards first_scan | done
                        # writes data/setup-state.json (resume point) + anonymous onboarding_step

Machine-side steps (this script):
  1. python   — 3.9+ (the python3 that ships with macOS is enough)
  2. venv     — ~/.jobkit/venv with pyyaml, python-docx, pypdf (shared by all projects, survives updates)
  3. pdf      — LibreOffice for PDF CVs (optional; prints the install command)
  4. folders  — me/, data/ from templates (never overwrites), .gitignore for me/ and data/
  5. perms    — .claude/settings.json in this folder: allow `jk` so the agent doesn't ask every time
  6. ping     — anonymous install event (telemetry.py), opt-out respected
Agent-side steps (/setup command): Chrome extension, CV + LinkedIn import, profile questions,
boards fit, first scan. Output is compact on purpose: the agent reads it.
"""
from __future__ import annotations

import contextlib
import json
import re
import os
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
PHASES = ["machine", "browser", "import", "profile", "boards", "first_scan"]
STATE = DATA / "setup-state.json"
results: dict[str, str] = {}


def _load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def phase(name: str, status: str = "done", reason: str = "") -> int:
    """Record an onboarding phase. Idempotent: re-marking a phase sends nothing new."""
    if name not in PHASES + ["done"]:
        print(f"unknown phase: {name}; one of: {' '.join(PHASES)} done")
        return 2
    import telemetry
    from datetime import datetime, timezone
    st = _load_state()
    now = datetime.now(timezone.utc)
    st.setdefault("started", now.isoformat(timespec="seconds"))
    if name != "done":
        for k in ("done", "skipped"):
            st[k] = [x for x in st.get(k, []) if x != name]
        st.setdefault("failed", {}).pop(name, None)
        if status == "fail":
            st["failed"][name] = telemetry.code(reason) or "unknown"
        else:
            st.setdefault("skipped" if status == "skip" else "done", []).append(name)
    minutes = round((now - datetime.fromisoformat(st["started"])).total_seconds() / 60)
    if name != "done" and [name, status] not in st.get("sent", []):
        st.setdefault("sent", []).append([name, status])
        telemetry.send("onboarding_step", {"step": name, "status": status, "order": PHASES.index(name) + 1,
                                           "reason": st.get("failed", {}).get(name), "minutes": minutes})
    finished = set(st.get("done", [])) | set(st.get("skipped", []))
    if (name == "done" or set(PHASES) <= finished) and not st.get("completed_at"):
        st["completed_at"] = now.isoformat(timespec="seconds")
        telemetry.send("onboarding_done", {"minutes": minutes, "skipped": st.get("skipped", []),
                                           "failed": sorted(st.get("failed", {})),
                                           "missing": [x for x in PHASES if x not in finished]})
    DATA.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1))
    left = [x for x in PHASES if x not in finished]
    note = f" ({st['failed'][name]})" if status == "fail" and name in st.get("failed", {}) else ""
    print(f"phase {name}: {status}{note} · left: {' '.join(left) if left else 'none'}")
    return 0


def step(name: str, ok: bool, note: str = "") -> bool:
    results[name] = ("ok" if ok else "FAIL") + (f" — {note}" if note else "")
    return ok


def has_deps(py: Path | str) -> bool:
    r = subprocess.run([str(py), "-c", "import yaml, docx, pypdf"], capture_output=True)
    return r.returncode == 0


def main() -> int:
    if "--phase" in sys.argv:
        i = sys.argv.index("--phase")
        name = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        if "--fail" in sys.argv:
            j = sys.argv.index("--fail")
            return phase(name, "fail", sys.argv[j + 1] if j + 1 < len(sys.argv) else "")
        return phase(name, "skip" if "--skip" in sys.argv else "done")
    first = not (ME / "profile.yaml").exists()
    step("python", sys.version_info >= (3, 9), platform_py())

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
    todo = sum(p.read_text(encoding="utf-8", errors="ignore").count("TODO") for p in ME.rglob("*")
               if p.is_file() and p.suffix.lower() in (".md", ".yaml", ".yml", ".txt")) if ME.exists() else -1
    step("folders", ME.exists() and DATA.exists(), f"{HOME} · TODO left in me/: {todo}")

    jk = FRAMEWORK / "scripts" / "jk.py"
    # Commands call `python3 "<root>/scripts/jk.py"` (quoted, the path may have spaces): allow both forms.
    rules = [f"Bash(python3 {jk}:*)", f'Bash(python3 "{jk}":*)']
    sp = HOME / ".claude" / "settings.json"
    try:
        cfg = json.loads(sp.read_text()) if sp.exists() else {}
    except ValueError:
        cfg = {}
    allow = cfg.setdefault("permissions", {}).setdefault("allow", [])
    stale = [r for r in allow if r.startswith("Bash(python3 ") and re.search(r'/scripts/jk\.py"?:\*\)$', r)
             and r not in rules]
    if all(r in allow for r in rules) and not stale:
        step("perms", True)
    elif CHECK:
        step("perms", False, "run: jk setup")
    else:
        cfg["permissions"]["allow"] = [r for r in allow if r not in stale] + [r for r in rules if r not in allow]
        sp.parent.mkdir(exist_ok=True)
        sp.write_text(json.dumps(cfg, indent=2) + "\n")
        step("perms", True, "updated after plugin move/update" if stale else "added")

    if not CHECK:
        try:
            import telemetry
            sent = telemetry.send("install", {"first": first, "py_kind": telemetry.py_kind(),
                                              "steps_ok": sum(v.startswith("ok") for v in results.values()),
                                              "steps_failed": [k for k, v in results.items() if v.startswith("FAIL")]})
            step("telemetry", True, ("on" if telemetry.enabled() else "off") + (", sent" if sent else ", queued"))
        except Exception as e:  # noqa: BLE001
            step("telemetry", True, f"skipped: {e}")

    if not CHECK and not any(v.startswith("FAIL") for v in results.values()) \
            and "machine" not in _load_state().get("done", []):
        try:
            with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
                phase("machine")
        except Exception:  # noqa: BLE001
            pass
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
