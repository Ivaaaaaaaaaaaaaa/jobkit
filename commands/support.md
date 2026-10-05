---
description: Support ticket — describe a problem with the kit, attach diagnostics, send to the maintainer
argument-hint: "[what went wrong]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Problem: $ARGUMENTS (empty → ask: what you did, what happened, what you expected).
1. Reproduce if cheap; if it's a usage question — answer it and stop.
2. `jk support draft "<problem in 2–5 sentences, no personal data>"` → show the draft.
3. Ask how to send: private (default, to the maintainer, not public) or GitHub issue (public).
4. On explicit OK: `jk support send <file> private|github` (github prints a link the user opens and submits).
