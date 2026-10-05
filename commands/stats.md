---
description: Metrics — funnel, response rates by track/source/score, usage; anonymized export
argument-hint: "[optional: 'share' to create an anonymized file]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
`jk stats` → explain in 3–5 short lines: where the funnel leaks, what works, one suggested change
(<5 applications per group = no conclusion). 'share' → `jk stats --share`, show the file path and
that it has no companies, roles, links or texts. `jk telemetry` shows the anonymous-stats status.
