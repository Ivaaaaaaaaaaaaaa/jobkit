# CV — writing and tailoring

Facts: `me/experience-bank.md`. Framing: `me/positioning.md`. Data: `me/cv/base.yaml`. Renderer: `jk cv`.

## Format
One page (< ~10 yrs experience), reverse-chronological, DOCX (PDF if the form/messenger needs it).
Blocks: name · contact line (title · city · phone · email · links) · Summary · Experience
(company — descriptor · location; title · dates; 2–4 bullets) · Projects (if it strengthens) ·
Skills (3–5 groups, each skill once) · Education (unfinished = "coursework") · languages/work rights if relevant.

## Bullets
1. First bullet = strongest business outcome, not an activity.
2. Result → how → tools; number first.
3. Every number has a baseline ("+40% vs manual process").
4. ≤4 per role, ≤2 lines each; unclear in one read → cut.
5. Show user work explicitly (interviews, feedback loops).
6. Outcome over effort ("turned X into Y", not "responsible for X"). No adjectives.

## Summary
About own experience, never "you/your". Answers the role's main need with proven experience. Each
strength tied to where it was proven. No filler (languages, "team player") unless the JD asks.
3–4 sentences, ≤ ~80 words. `jk audit --kind summary`.

## Skills
Lead with the group the role values. Drop level-obvious items (Agile, Scrum, MS Office).

## Tailoring per vacancy — what changes
Title (level/domain within the track) · summary (track template + 3–5 exact JD keywords) · bullet
selection/order · skill group order · past-job title only from `title_options` (renderer enforces).
```
data/applications/<id>/jd.md      # copy of the posting (they disappear)
data/applications/<id>/cv.yaml    # overlay:
title: "Product Manager · Growth"
summary: >
  ...
experience: {"Company A": [2, 0, 1]}
skills_order: ["Growth & Analytics", "Product", "Tools"]
file_name: "Name Surname CV"
```
`jk audit --kind summary --text "…"` → `jk cv data/applications/<id>/cv.yaml [--pdf]`.
File name human-readable ("Name Surname CV"), never "cv_final_v3".

## ATS readability
No tables/columns/icons in content (renderer keeps it plain), standard headings, one date format
("Mar 2023 – Present"), JD keywords in text when true.

## Before upload
one page (renderer warns) · title/summary tailored, no "you" · `jk audit` clean · no banned claims ·
links work · human file name · open the file and look.
