---
description: Apply to one role — tailored CV and letter, form filled up to the submit button
argument-hint: "<vacancy link or tracker id>"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Role: $ARGUMENTS. Forms: playbooks/forms.md.
1. Find/add in tracker. `jk t check "Co::Role" <url>` — ⛔ → stop and say why.
2. Gates on the real ATS (scoring.md §1); open the form before tailoring. Skipped → record, stop.
3. Score (match, evidence, track). Low → say so, ask whether to proceed.
4. CV: overlay by track (cv-guide.md) → `jk audit --kind summary` → `jk cv <overlay>` (+`--pdf` if the form wants PDF).
5. Letter/answers if the form has fields: brief → letter (cover-letter.md) → `jk audit --kind letter --company X`; answers.md, each audited.
6. By submit_mode: draft_only → give paths, stop. Else: Chrome tools, new tab, fill everything, attach CV, run formcheck.
7. confirm_each → stop before Submit, report line, "waiting for confirmation". auto_high and eligible → submit.
   After sending: "thank you" screen, `jk t set <id> applied --next follow-up --date <+7d>`, close tab.
8. New form question + answer → application-answers §5.
