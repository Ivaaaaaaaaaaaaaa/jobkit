# Gates and scoring

A flat "gut" 1–10 clusters at 7–8 and gives no order. Here the score is earned by evidence and
freshness breaks ties.

## 1. Gates (cheap first, before any CV)
| # | Gate | Check | Skip when |
|---|---|---|---|
| 1 | Duplicate | `jk t check "Co::Role" <url>` | ⛔, or same role under another name; one role posted in N countries = one role |
| 2 | Alive | open the company ATS link | 404, "filled", not on the board |
| 3 | Role & level | title + first paragraphs | other discipline in a "product" title; level 2 steps off |
| 4 | Geo | JD text + form on the ATS + where the employer and recruiter sit | "must reside in X", office outside list, region without work rights, employer in `skip_employer_countries` (even for "remote from anywhere"); region list without your country → `geo.region_list_policy` |
| 5 | Hard requirements | Requirements block | mandatory language, citizenship, "N yrs in domain X", tool — missing. "Nice to have" doesn't skip |
| 6 | Money | published band | band minimum < `salary.floor_year` (no band ≠ skip) |
| 7 | Exclusions | `skip_companies` | listed |
| 8 | Form | open it | school grades, video, SMS, account → end of queue; login wall on an aggregator (Djinni, DOU, local boards) → find the same role on the company ATS first |
| 9 | Limits | form header, tracker | "max N applications per 60 days" reached |

Aggregators lie about geo ("Remote" = one country) and date (date they found it, or a paid "bump"
of an old post). Trust the company ATS.

Region list without your country ("Remote in EU: Germany, Spain, Portugal…"): `region_list_policy:
skip` (default) drops it; `apply` keeps it — then every location question is answered truthfully
(your real country, "None of the above", "No"). Never pick a country you don't live in. A required
field with only listed countries and no honest option → skip.

## 2. Rubric (per role that passed)
```
match 0–100   core of the JD vs PROVEN experience
freshness 0–10
evidence      a concrete fact from me/experience-bank.md
track         from me/positioning.md
why           one sentence
```
rank = match + 1.5 × freshness (queue order). Tracker score = round(match/10).

match: 85–100 core = strongest recent proven story · 70–84 strong, proof one notch off (older,
adjacent domain, level ±1) · 56–69 genuine but partial · ≤55 weak/unproven. **No evidence → ≤55.**
Reward in the order of tracks in positioning; penalize generic roles with no hook and other
disciplines under a product title.

freshness: ≤1d 10 · ≤2d 8 · ≤4d 6 · ≤7d 4 · ≤14d 2 · older/unknown 1. A fresh 78 beats a stale 82.

## 3. Levels
high 8–10 → full tailoring, first; `auto_high` may submit. medium 5–7 → tailor, note the doubt.
low ≤4 → no CV, `skipped` with reason.

## 4. Record
`jk t add --company X --role Y --url <ats> --source ats:greenhouse --location "Remote, EMEA" --posted-days 3 --score 8 --track A --comment "evidence: …; why: …"`
Skipped: `--status skipped --comment "gate 4: must reside in Germany"`.
