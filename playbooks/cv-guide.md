# CV — writing and tailoring

Facts: `me/experience-bank.md`. Framing: `me/positioning.md`. Data: `me/cv/base.yaml`. Renderer: `jk cv`.

## One version of every number
Recruiters put the CV next to LinkedIn and next to what you said on the call. Two versions of one
number ("5 products" here, "10 products" there) read as a lie, even when both were true once.
```
experience-bank ──► me/cv/base.yaml ──► tailored CV
       └──────────► LinkedIn profile ──► me/linkedin.md (copy of its text)
```
- The bank holds the current public numbers. A number changes → the same day: bank, base.yaml,
  LinkedIn profile and `me/linkedin.md`.
- The old wording goes to `banned_claims`, so `jk audit` catches it in any text later.
- Check: `jk audit --file me/linkedin.md` (numbers must exist in the bank, no banned claims).
- Same numbers in letters, form answers and on the call (interview-prep.md §0).

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
3–4 sentences, ≤ ~80 words (~520 characters — check the length before rendering, not after).
Open with the current job's strongest result. `jk audit --kind summary`.

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
File name human-readable ("Name Surname CV"), never "cv_final_v3", and never another company's
name: a file called "acme-cv.pdf" sent to Beta tells Beta it's a mass mailing. For messages keep a
copy named "Name-Surname-CV-<role>.pdf".

## ATS readability
No tables/columns/icons in content (renderer keeps it plain), standard headings, one date format
("Mar 2023 – Present"), JD keywords in text when true.

## Before upload
one page (renderer warns) · title/summary tailored, no "you" · `jk audit` clean · no banned claims ·
links work · human file name · open the file and look.
