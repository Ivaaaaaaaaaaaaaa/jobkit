---
description: Experience interview — per-job questions, numbers, STAR stories, CV variants
argument-hint: "[optional: company or topic to start with; 'stories' = interview stories only]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Goal: every achievement in `me/experience-bank.md` has a result with a number (or "≈" + how
estimated); 6–8 STAR stories; "What I don't have" filled. Question bank: playbooks/cv-questions.md.
Focus: $ARGUMENTS (empty = all jobs, newest first).

1. Read bank, base.yaml, profile. List gaps, show the plan (which jobs, ~how many questions).
2. One job at a time: A context → B achievements → C tools → D stories. Ask only where empty, 2–4 per message.
3. Turn each answer into a bullet "result → how → tools", show it. No number → section E. "We did" → ask what *you* did.
4. Junior / career switch → section F.
5. After each job: write bank + base.yaml. Things they lack → bank §7 + banned_claims.
6. End: propose CV variants (section G), `jk cv --pdf`, `jk audit --kind summary` on the summary, show file.
Never invent a number.
