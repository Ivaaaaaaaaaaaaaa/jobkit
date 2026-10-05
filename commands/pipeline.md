---
description: Pipeline — funnel, who replied, what's due, update statuses from plain text
argument-hint: "[optional news, e.g. 'Acme rejected, Beta interview Thursday']"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Input: $ARGUMENTS
1. News → find roles, `jk t set <id> <status> "<comment>" --next "<step>" --date <date>`. Ambiguous → one question.
2. `jk t funnel` and `jk t due`; for each follow-up a draft (contacts.md §5).
3. 20+ applications → `jk stats`: what tracks/sources/levels get replies; suggest one change.
