#!/usr/bin/env python3
"""jobkit CLI — one entry point for the agent and the human.

    python3 <kit>/scripts/jk.py <command> [args]

  setup [--check]        install/check environment, folders, permissions (doctor = setup --check)
  import <file> [--as linkedin]   CV / LinkedIn PDF -> text in data/import/
  boards [--dry]         fit company boards to profile + geo -> me/boards.txt
  scan [--days N] [--to-tracker] [--top N]   find fresh jobs
  t <add|check|set|list|funnel|due> ...      tracker (data/tracker.csv)
  cv [overlay.yaml] [--pdf]                  render CV
  audit --text "..." [--kind summary|letter|answer] [--company X]
  formcheck              print the form readiness test (paste into javascript_tool)
  stats [--share|--json] usage & outcome metrics
  support draft "..." | support send <file> private|github
  telemetry [on|off|status|flush]
  test                   offline self-tests + end-to-end smoke on a fixture persona
Runs itself inside ~/.jobkit/venv when it exists, so system Python needs no packages.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VPY = Path.home() / ".jobkit" / "venv" / "bin" / "python"
MAP = {"setup": "setup.py", "doctor": "setup.py", "import": "import_cv.py", "boards": "boards_fit.py",
       "scan": "scan.py", "t": "tracker.py", "tracker": "tracker.py", "cv": "render_cv.py",
       "audit": "text_audit.py", "stats": "metrics.py", "support": "support.py",
       "telemetry": "telemetry.py", "test": "selftest.py"}

if VPY.exists() and Path(sys.executable).resolve() != VPY.resolve() and not os.environ.get("JK_NO_VENV"):
    os.execv(str(VPY), [str(VPY), __file__, *sys.argv[1:]])

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
    print(__doc__)
    sys.exit(0)
cmd, rest = sys.argv[1], sys.argv[2:]
if cmd == "formcheck":
    print((HERE / "form_check.js").read_text())
    sys.exit(0)
if cmd == "doctor":
    rest = ["--check", *rest]
if cmd not in MAP:
    print(f"unknown command: {cmd}\n{__doc__}")
    sys.exit(2)
sys.exit(subprocess.call([sys.executable, str(HERE / MAP[cmd]), *rest]))
