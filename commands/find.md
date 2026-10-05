---
description: Find jobs — fresh scan, gates on the real ATS, scoring, queue into the tracker (no applying)
argument-hint: "[optional filter, e.g. 'remote EU only', 'growth', '7 days']"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Filter: $ARGUMENTS. Gates and rubric: playbooks/scoring.md. Sources: playbooks/job-sources.md.
1. `jk scan --top 30` (`--days N` if asked). Apply the filter while reviewing.
2. Few results or asked → manual channels (job-sources §3; LinkedIn only by browsing).
3. For wide/check candidates: open on the company ATS, read the JD, gates 2–8; save JD to data/applications/<id>/jd.md.
4. Score passers: match, freshness, evidence, track, why.
5. Tracker: passers `found` with score/track; skipped with "gate N: reason".
6. Report: sources → filters → gates (where they dropped) → top by rank (company · role · geo · score · track · why). Next: /jobkit:apply <id> or /jobkit:jobs-run.
Few results → fix the source (job-sources §5), don't recycle stale roles.
