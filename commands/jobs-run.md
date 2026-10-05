---
description: Full run — fresh search, gates, queue, CVs and forms in a batch, statuses, report
argument-hint: "[number of applications; default search.per_run]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Count: $ARGUMENTS (default `search.per_run`). One status line after each step.
0. `jk setup --check` clean; no TODO in contacts/target/geo/salary (else ask). Chrome tools with file_upload (forms.md §0) — missing → draft_only, say so.
1. `jk t due` — follow-ups/deadlines; one question about statuses they may not have reported.
2. Fresh search as /jobkit:find. Fresh beats stale.
3. Queue: top by rank up to count (+medium if high is short). Batch dedup: `jk t check "A::R" <u> "B::R" <u> ...`.
4. Tailor in batch: overlay → audit → render; brief → letter → audit; answers. Status ready.
5. Forms one tab per role, fill all, CV, formcheck. Captcha roles last. Submit per submit_mode.
6. Report (SKILL.md "Report after a run").
7. After confirmation: send if asked, check "thank you", `jk t set <id> applied --next follow-up --date <+7d>`, close tabs one by one.
