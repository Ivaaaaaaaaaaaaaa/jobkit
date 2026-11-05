"""Where things live. FRAMEWORK = this code (a copied folder or an installed plugin).
HOME = the user's working folder with me/ and data/: $JOBKIT_HOME, else the Claude project dir, else cwd."""
import os
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("JOBKIT_HOME") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
ME = HOME / "me"
DATA = HOME / "data"
VERSION = (FRAMEWORK / "VERSION").read_text().strip() if (FRAMEWORK / "VERSION").exists() else "dev"


def _crash_hook(kind, exc, tb):
    """Uncaught error in a jk script → print as usual, then an anonymous crash event (telemetry.py)."""
    sys.__excepthook__(kind, exc, tb)
    if kind in (KeyboardInterrupt, SystemExit):
        return
    try:
        import telemetry
        telemetry.report_crash(Path(sys.argv[0]).name, exc)
    except Exception:
        pass


import sys  # noqa: E402
if Path(sys.argv[0]).resolve().parent == FRAMEWORK / "scripts" and not os.environ.get("JK_NO_CRASH_REPORT"):
    sys.excepthook = _crash_hook
