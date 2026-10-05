# Data storage

## Layers
- **Framework** (shared, updatable): plugin code — skills, commands, playbooks, scripts, templates, config.
- **Personal** `me/`: profile.yaml, experience-bank.md, positioning.md, application-answers.md, cv/, boards.txt.
- **Working** `data/`: tracker.csv, applications/<id>/ (jd, brief, cv.yaml, CV, letter, answers,
  prep), import/, events.jsonl, telemetry.json, support/.
`me/` and `data/` are gitignored and live in the candidate's folder; plugin updates never touch them.
Backup = copy both (cloud drive at the user's discretion: they contain phone, address, salary).

## Rules
- One fact, one place: numbers about self → bank; form answers → application-answers; settings → profile.
- Tracker is the truth about vacancies — not notes, not agent memory.
- Every found role is recorded immediately (`found`), before tailoring.
- The application folder keeps exactly what was sent; save the JD (postings disappear).

## Tracker columns
id, company, role, url, source, location, found_at, posted_days, score, track, status, applied_at,
next_action, next_date, cv_path, comment, updated_at. Opens in Excel/Numbers/Sheets; don't rename
headers; don't keep it open while the agent writes.

## Other backends (same columns)
Google Sheets: import the CSV, or connect a Sheets/Drive connector and keep the CSV as local cache
for dedup. Notion: database with these columns (status = Status type), Notion connector with the
user's PERSONAL account, `tracker.backend: notion`, `tracker.notion_database: <url>`; dedup by query,
rows named "Company — Role". Before any connector write — confirm it's the user's own account.

## Job-search mailbox
A separate address keeps replies tidy. Connected to Claude (Gmail connector) the agent can update
statuses from replies, fetch ATS verification codes/links (only from the company or its ATS domain),
draft answers. Sending only on explicit request.

## Telemetry (anonymous)
`data/telemetry.json` holds a random install id. Sent: install pings, a monthly counts snapshot,
support tickets the user confirms. Never: names, contacts, companies, roles, links, CV/letter text.
`jk telemetry off` disables; `jk telemetry` shows status and queue.
