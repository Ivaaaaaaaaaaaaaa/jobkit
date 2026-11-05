---
description: After an interview — debrief from the transcript, mistakes count, better answers, follow-up draft
argument-hint: "<company or tracker id> [path to transcript or notes]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Target: $ARGUMENTS. Script: playbooks/interview-prep.md §0.
1. Find the call folder `data/interviews/<date>-<company>-<stage>/` (create it if missing). Get the
   transcript: the given file, a recorder export, or ask the candidate for notes once.
   Save as transcript.md (rename the candidate's speaker label only).
2. debrief.md: score /10 with one line why; table said / why weak / better (max 6 rows, worst
   first); what we learned (team, metrics, process, money, next stage); follow-up draft
   (contacts.md §5) — sent only on the candidate's "ok".
3. me/interview-mistakes.md: each open mistake +1 (with link) or "clean <date>"; new ones as rows.
4. me/interview-answers.md: better version of each weak answer, dated. New facts → experience-bank
   (ask before adding a number).
5. Tracker: `jk t set <id> <status> "<stage> done" --next "<next step>" --date <date>`.
6. Show: score, top 3 fixes for the next call, the follow-up draft.
