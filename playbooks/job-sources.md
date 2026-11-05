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
Point Nine, Sequoia, MMC, HV Capital, Seedcamp, Speedinvest…), YC Work at a Startup, competitors of
companies in the queue, LinkedIn feed, companies that the aggregators below keep showing.

## 3. Manual channels
| Channel | How | Note |
|---|---|---|
| LinkedIn Jobs | candidate's Chrome, Past week + Remote + level, sorted by date | see §3a |
| LinkedIn posts | search posts "hiring product manager" + region | jobs that aren't on boards; read only |
| Telegram job channels | public preview without login: `https://t.me/s/<channel>` (older: `?before=<post id>`) | often a recruiter contact → contacts.md |
| SmartRecruiters, all companies | JSON `https://jobs.smartrecruiters.com/sr-jobs/search?keyword="product manager"&locationType=remote&limit=100` (phrase in quotes; 100 newest, no paging) | real ATS links |
| Remote.com Jobs | `https://remote.com/jobs/all?query=<role>&page=N` | lists included countries; apply link goes to the ATS |
| EU Remote Jobs | `https://euremotejobs.com/job-tag/<tag>/` | regions in the listing; Apply → ATS |
| Himalayas, 4dayweek, Wellfound | browser | Himalayas lists honest countries |
| Niche boards | by domain (crypto, climate, AI, games) | ask the candidate |
| Referrals | candidate's network | highest conversion — ask weekly |
| Local sites | hh.ru, getmatch, Habr Career, Djinni, DOU, StepStone, Welcome to the Jungle… | by market; see §3b |

### 3a. LinkedIn Jobs
- Open a job as `https://www.linkedin.com/jobs/search/?currentJobId=<id>`, never `/jobs/view/<id>`:
  after ~40 views `/jobs/view` comes back without the description, the search panel still shows it.
  `jk lijob` prints a reader for that panel → paste into javascript_tool → company, title, meta,
  apply type (easy/external/applied), JD. Empty JD → read it on the company ATS.
- Go through every page of the date window, not only the first 25 cards. Read the visible list
  with `get_page_text`, page by page, at a human pace. The list renders lazily and only in the
  visible tab — make the tab active first, scroll the list.
- One role posted in N countries is one role (dedup by company + title).
- Reading the candidate's own browser one page at a time is fine; bulk scraping LinkedIn is not.

### 3b. Local boards — traps
- **Djinni** (Ukraine/Eastern Europe tech): RSS `https://djinni.co/jobs/rss/?primary_keyword=<Role>`.
  RSS and JSON-LD carry the date of the last "bump", not the post: take the "Published …" line on
  the page. In one check half of the "fresh" roles were old posts lifted to the top.
- **DOU** (jobs.dou.ua): RSS `https://jobs.dou.ua/vacancies/feeds/?category=<Category>` with
  `&remote`, `&relocation`, `&city=<city>`.
- Djinni, DOU and most local boards accept applications only from a logged-in candidate. Use them
  to discover: take company + role, then find the form on the company ATS.
- **hh.ru / Habr Career / getmatch** — login-only apply too; the candidate applies, or find the ATS.

## 4. Don't
WeWorkRemotely ("Anywhere" on nearly all, de facto US) · Indeed/Glassdoor/ZipRecruiter (block bots) ·
aggregators hiding the company without login (can't dedup).

## 5. Few results → fix the source
Widen `title_include` (synonyms), check `title_exclude` · add companies to boards · `max_age_days` 21
(fresh still first) · add local sites.

## 6. Keep a channel log
After 20+ applications look at `jk stats`: replies per source. The channel that gives replies gets
more time; the one that gives only duplicates and wrong geo gets less. Searching the same sources
in circles is the main time sink — one scan per day into the queue, then only apply from it.
