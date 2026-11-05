# Interview prep and debrief (/jobkit:interview-prep, /jobkit:debrief)

## 0. The loop — every call makes the next one better
```
before ──► prep.md ──► call ──► transcript.md ──► debrief.md
   ▲                                                  │
   └──── me/interview-mistakes.md · me/interview-answers.md ◄──┘
```
One folder per call: `data/interviews/<YYYY-MM-DD>-<company>-<stage>/` with `prep.md`,
`transcript.md` (as is; only rename the candidate's speaker label), `debrief.md`.
- **Before:** prep.md from `me/interview-answers.md` + company research (§1). At the very top — every
  mistake from `me/interview-mistakes.md` with count ≥ 1, one line each. The candidate reads the
  60-second pitch aloud 3 times.
- **After:** transcript from the recorder (Zoom/Meet/Granola/Otter export) or the candidate's notes →
  `debrief.md`: score /10; table "said / why weak / better"; what we learned about the company and
  the next stage; follow-up draft. Then each mistake in `me/interview-mistakes.md` gets +1 or
  "clean <date>"; a new one gets a new row; three "clean" in a row → closed. A weak answer gets a
  better version with a date in `me/interview-answers.md`. Tracker: status + next step.
- Numbers on the call = the bank = the CV = LinkedIn. A new number said on a call goes to the bank
  first, or isn't said.

## 0a. Mistakes that repeat for most candidates (check in every debrief)
No ready pitch, no numbers · a direct question about a number answered with another story (no
"how measured", no before/after) · a story that never reaches its result — end with "Result: …" ·
filler words (basically, like, you know) — a pause instead · no question about their main metric
and next step · numbers that differ from the CV · negative words about the current employer or
founders when asked "why leaving" · agreeing with the interviewer's doubt ("so you're more of an
engineer?" — "yes") instead of holding the position · arguing with an opinion instead of a number ·
several salary numbers in a row, the anchor drops · a personal-life example for a work question ·
the call display name shows a company or nickname, not "Name Surname" · in regulated companies,
casual words about data ("everything goes to GitHub, I have access to all").


## 1. Collect → data/interviews/<date>-<company>-<stage>/prep.md
Company (product, customers, business model, stage/funding, size, last-6-months news, competitors —
site, blog, LinkedIn, Crunchbase, reviews, app stores) · product hands-on (free signup by the
candidate; 3 strengths, 3 problems, 1 idea with hypothesis + metric) · top-5 requirements → STAR
story each · interviewers' backgrounds · gaps → honest "what I lack and what instead".

## 2. Stages
| Stage | Tests | Prepare |
|---|---|---|
| Recruiter | motivation, money, timing, fit | 60-s pitch, why us, band (answers §3), notice |
| Hiring manager | experience, thinking, level | 5–6 STAR stories, questions |
| Product sense / case | structure | user → problem → solutions → priority → metric |
| Metrics | data | north star, metric tree, "metric fell 10% — what do you do" |
| Execution | prioritization, conflict, deadlines | those stories |
| Take-home | quality, speed | clarify scope/criteria; ≤4–6 h; ship with a summary |
| Final / CEO | values, ambition | 90-day plan, strategy questions |

## 3. Common questions → bullet answers from the bank
About yourself (60–90 s) · why leaving · best launch / biggest failure · prioritization + saying no ·
working with eng/design/data · how you know a feature worked · product you love · 2–3 years plan ·
salary (ask their band first, then answers §3).

## 4. Questions to them (pick 3–5)
Main team metric and its trend · what makes the hire successful in 90 days · who has the final say ·
why the role is open · how discovery works · biggest product problem now.

## 5. Mock
5–7 stage questions; after each: what was strong, what lacked (numbers, structure, "I" vs "we"),
an improved answer. New facts → bank.

## 6. After
debrief (§0) · `jk t set <id> interview "<stage>; next …" --next follow-up --date <tomorrow>` ·
thank-you draft (contacts.md §5) · good answers → interview-answers / bank / application-answers.

## 7. Offer
Compare with target/floor; compute take-home; clarify base/bonus/equity, probation, format, leave,
equipment. Negotiate with facts (other offers, market, rare experience). Only the candidate accepts and signs.
