"""Where things live. FRAMEWORK = this code (a copied folder or an installed plugin).
HOME = the user's working folder with me/ and data/: $JOBKIT_HOME, else the Claude project dir, else cwd."""
import os
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("JOBKIT_HOME") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
ME = HOME / "me"
DATA = HOME / "data"
VERSION = (FRAMEWORK / "VERSION").read_text().strip() if (FRAMEWORK / "VERSION").exists() else "dev"
