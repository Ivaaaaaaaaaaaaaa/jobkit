# Job sources

Trust the company ATS, not aggregators: they label one-country jobs "Remote" and show the date
they found the job. Aggregator = discover; ATS = verify geo/date and apply.

## 1. Built into `jk scan` (no keys, no browser)
| Source | Gives | Honest geo? |
|---|---|---|
| `ats` — boards from me/boards.txt (or config/ats_orgs.txt) | real forms, company dates | yes, still verify "Remote" |
| `jobicy` | remote, much Europe | yes |
| `remoteok` | remote, much US | partly |
| `remotive` | remote, broad | partly |
Toggle via `search.sources`; tags via `search.board_tags`.

## 2. Company boards — the most productive channel
`jk boards` fits the seed list to the profile and geo → `me/boards.txt`. Grow it under `# mine`:
1. Interesting company → careers page → engine + slug from the URL: `jobs.ashbyhq.com/acme` →
   `ashby acme`; `job-boards.greenhouse.io/acme` → `greenhouse acme`; `jobs.lever.co/acme` →
   `lever acme`; `apply.workable.com/acme` → `workable acme`; `acme.recruitee.com` → `recruitee acme`.
2. Verify: `curl -s https://api.ashbyhq.com/posting-api/job-board/<slug> | head -c 200` (non-empty = ok).
3. Add the line, re-run `jk boards`.
Where to find companies: VC portfolio job boards (Getro/Consider: Accel, Index, Atomico, Balderton,
Point Nine, Sequoia…), YC Work at a Startup, competitors of companies in the queue, LinkedIn feed.

## 3. Manual channels
| Channel | How | Note |
|---|---|---|
| LinkedIn Jobs | candidate's Chrome, Past week + Remote + level | never scrape; after ~40 views texts stop loading — read JD on the ATS |
| LinkedIn posts | search posts "hiring product manager" + region | jobs that aren't on boards; read only |
| Telegram job channels | by niche/region | often a recruiter contact → contacts.md |
| Himalayas, 4dayweek, Wellfound | browser | Himalayas lists honest countries |
| Niche boards | by domain (crypto, climate, AI, games) | ask the candidate |
| Referrals | candidate's network | highest conversion — ask weekly |
| Local sites | hh.ru, getmatch, Habr Career, Djinni, StepStone, Welcome to the Jungle… | by market |

## 4. Don't
WeWorkRemotely ("Anywhere" on nearly all, de facto US) · Indeed/Glassdoor/ZipRecruiter (block bots) ·
aggregators hiding the company without login (can't dedup).

## 5. Few results → fix the source
Widen `title_include` (synonyms), check `title_exclude` · add companies to boards · `max_age_days` 21
(fresh still first) · add local sites.
