# Onboarding script (used by /jobkit:setup)

Goal: in 30–60 min of conversation fill `me/` so later runs need no questions. Resumable:
`data/setup-state.json` lists finished phases (`jk setup --phase <name>` writes it).

## Phase 0 — how it works (first run, 1 minute)
Before any question show the scheme and the "does / never does" lists from `GUIDE.md` (plugin
root), in the user's language, ≤10 lines. The user should know: what the agent does alone, what
stays theirs (Submit, messages, passwords), where data lives, that stats are anonymous.
At the end of onboarding show the daily routine from the same file.

## How to talk
- Friendly, businesslike, no judgement — job search is stressful.
- One phase at a time, 3–6 questions. Take what exists (CV, LinkedIn) first, ask only gaps.
- After each phase write files and show a short summary: "correct me if wrong".
- Unknown answer → propose a default, mark TODO, move on.
- Sensitive (citizenship, money): say why and where it's stored ("only in me/ on this computer").

## Browser
Forms need the Claude in Chrome extension: Chrome Web Store → "Claude" → install → sign in with the
same Claude account → allow. Check with ToolSearch `claude-in-chrome` + `tabs_context_mcp`.

## Phase 1 — what exists
CV file, LinkedIn PDF (Profile → More → Save to PDF), portfolio/case links, previous applications
(table → `jk t add ... --status applied` each, so we never apply twice). `jk import` each file,
then fill bank + base.yaml; show "found 4 jobs, 11 achievements, 6 with numbers; gaps: …".

## Phase 2 — who and what → profile: name, target, search
Name (Latin, as on LinkedIn) · target roles (offer options from experience) · honest level, stretch
up? · domains wanted / avoided · company stage. Build `title_include` / `title_exclude`, show them.

## Phase 3 — where and how much → geo, work_authorization, salary, contacts
Current city · formats (remote/hybrid/office + cities) · relocation and where · "remote in <region>"
roles that list countries without yours — skip or apply honestly (`geo.region_list_policy`) ·
countries whose employers to skip (`skip_employer_countries`) · citizenship, where they can work
without a visa, contractor entity? · salary: currency, period, gross/net, target, floor
(don't know the market → offer a quick estimate from 20–30 postings with published bands) ·
contacts (recommend a separate job-search email), phone in international format.
Fill application-answers §1–3 incl. three salary tiers (≈ +10–15% / target / −10–15%), user edits.

## Phase 4 — how we work → autonomy, skip_companies, banned_claims
Who presses Submit (recommend `confirm_each` for the first 1–2 weeks, then `auto_high` or
`auto_all` once the candidate trusts the forms) · applications per run ·
companies to skip (ex-employers, past rejections) · what they do NOT have → banned_claims + bank §7
(typical: "managed a team", "SQL", "B2B", "machine learning") · tracker backend (csv default;
playbooks/data-storage.md).

## Phase 5 — optional, after the first applications
LinkedIn text → `me/linkedin.md` (paste from the profile) and `jk audit --file me/linkedin.md`:
same numbers as the CV. Interview files `me/interview-answers.md` (pitch, why leaving, money) —
fill before the first call.

## Done when
profile has no TODO in name, contacts.email/phone/city, target.roles/seniority, search.title_include,
geo.formats, work_authorization.can_work_in, autonomy; application-answers §1–2 filled; bank has
jobs with dates; `jk setup --check` has no FAIL.
