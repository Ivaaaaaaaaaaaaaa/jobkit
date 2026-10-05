---
description: Positioning — 2–4 evidence-backed tracks with titles, summaries, stories and CV variants
argument-hint: "[optional: role/vacancy to think about; 'review' = re-check by application results]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Library: playbooks/positioning-library.md. Write to `me/positioning.md`. Context: $ARGUMENTS
1. Read bank, profile, current positioning. Bank nearly empty → suggest /jobkit:cv-interview (or a 10-question short version).
2. Pick 5–8 strongest facts; table: track · evidence count · market width · risk.
3. Offer 2–4 tracks (first = default): title + fallbacks, one-liner, 2–3 summary variants in different voices, lead stories, don't-volunteer, keywords.
4. User picks (AskUserQuestion). Write. Add salary tier per track and 1–2 test hypotheses.
5. Per track: `me/cv/variant-<track>.yaml` overlay → `jk cv <file>` → show.
6. 'review': `jk stats` → response rate by track; <15 applications per track = no conclusion, say so.
No track without evidence. No invented titles.
