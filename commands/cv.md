---
description: Build a CV — base, track variant, or for a specific vacancy (DOCX/PDF)
argument-hint: "[empty = base | track name | vacancy link or id]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Request: $ARGUMENTS. Guide: playbooks/cv-guide.md.
Empty → `jk cv --pdf`. Track → `me/cv/variant-<track>.yaml` (create) → `jk cv <file>`. Vacancy →
`data/applications/<id>/cv.yaml` (title, summary with 3–5 JD keywords, bullet/skill order) → render.
Audit the summary first; after rendering check ≤1 page, open the file, give the path. Facts from the bank only.
