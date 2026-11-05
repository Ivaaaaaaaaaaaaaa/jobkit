# Changelog

## 0.3.0 — 2026-11-05
A month of daily real use folded back in.
- Forms: background-tab recipes (insertText, native setter, pointer-event chain, react-select
  `selectOption`, no timers in hidden tabs); new engines — Gem, JOIN, HR-Manager/Talentech, Breezy,
  Gravity Forms; Lever, Greenhouse, Ashby, Rippling and LinkedIn Easy Apply traps (shadow-DOM upload).
- `jk formcheck`: picks the largest form (not the site search), groups Lever radio labels, warns
  when zero required fields is not proof.
- LinkedIn Jobs: open via `currentJobId` (full JD after the ~40-view limit), `jk lijob` panel reader,
  all pages of the window, one role in N countries = one.
- Sources: SmartRecruiters all-company search, Remote.com, EU Remote Jobs, Telegram public preview,
  Djinni/DOU with the "bump" date trap; +23 verified company boards.
- Replies first: unanswered interview invitations open every run, with reply drafts.
- One version of every number: CV = LinkedIn = letters = calls (`me/linkedin.md`, audited).
- Interviews: prep → transcript → debrief loop, `/jobkit:debrief`, `me/interview-mistakes.md` with
  counts, `me/interview-answers.md`.
- Essays: "why us", "something you built", "what to do first" skeletons; personal stories bank.
- Gates: `geo.region_list_policy`, `skip_employer_countries`; submit mode `auto_all`.
- `jk t today` — the sent count comes from the tracker, not from memory.
- Python 3.9+ (stock macOS python3 is enough).
- Onboarding: "how it works" first (GUIDE.md, shown by /jobkit:setup), resumable phases via
  `jk setup --phase`, daily routine at the end; `/jobkit:debrief`.
- Analytics (anonymous, counts only): onboarding_step / onboarding_done funnel, daily_active,
  milestones (first scan → application → response → interview → offer), crash reports (script,
  exception type, line — no message), Python kind on install. Opt-out also works from the prompt hook.

### Fixed
- Stock macOS python: the CLI never switched into its venv (symlinked interpreter) — every command failed.
- `jk scan` second run wiped the queue beyond `--top`; empty `search:`/`geo:` crashed it.
- Tracker: `?id=1` and `?id=2` were one job; site-local job ids collided across companies; non-ASCII
  company/role gave an empty id; funnel response rate counted skipped leads.
- `jk setup`/`doctor` crashed once a DOCX/PDF was in me/; allow rule didn't match the quoted command.
- Telemetry ignored `telemetry: false` in the profile when run from the hook (no PyYAML there);
  a slow network could lose milestones.
- Audit: false alarms on phone numbers, "24/7", dates, "In 2024.", "30 kids"; banned "C++"/".NET" missed.
- Geo: "Remote - U.S.", North/Latin America, Americas, Australia passed as wide.
- Dates with "+0000" or odd fractions read as "fresh" on Python 3.9.
- `# mine` header line in me/boards.txt became a fake board; `jk import --as cv <file>` failed.
- Support ticket carried the OS username in paths; formcheck took "Accepted: .pdf" for an attached file.
- Per-track/source response rates ignored rejections; `jk stats --share` without data/; `jk cv` with
  a missing overlay or an unfilled name; 77 dead company boards in the seed list.

## 0.2.0 — 2026-10-05
- Packaged as a Claude Code plugin (marketplace install, `/jobkit:*` commands, lazy skill instead of CLAUDE.md).
- `jk` single CLI; `jk setup` installs its own venv, folders, permissions; idempotent.
- CV/LinkedIn import (`jk import`), board fitting to profile and geo (`jk boards`).
- Local metrics (`jk stats`), anonymous telemetry (install, monthly snapshot), support tickets.
- Agent-facing text in compact English (~3× fewer tokens); geo gate: "Remote - US" no longer passes.
- Offline e2e test on a fictional persona; CI; agent evals.

## 0.1.0 — 2026-10-04
- First version: rules, playbooks, tracker, scan, CV renderer, text audit.
