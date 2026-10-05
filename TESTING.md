# Testing jobkit

Three levels, cheapest first.

## 1. Scripts — offline, 5 seconds (also in CI)
```bash
python3 scripts/jk.py test
```
Unit self-tests + end-to-end smoke on the fictional persona `tests/fixtures/persona` in a temp
folder: setup → import → CV render → audit → tracker → metrics share (asserts no company/URL leaks).

## 2. Agent evals — `claude plugin eval`
```bash
claude plugin eval . --runs 3 --report evals-report.html
```
Cases in `evals/`: setup on the persona without a human, refusing an invented number, dedup
stopping a second application. Grader field names beyond `type` are drafts — check
`claude plugin eval --help` on first run and adjust.

## 3. Acceptance test — paste into a fresh Claude Code session

Create an empty folder, install the plugin, open the folder, paste:

```
Acceptance test of the jobkit plugin. You are the agent AND you play the candidate: take every
answer from ${CLAUDE_PLUGIN_ROOT}/tests/fixtures/persona/answers.md and the CV from
${CLAUDE_PLUGIN_ROOT}/tests/fixtures/persona/cv.md. Never ask me anything. Never press Submit,
never send messages (submit_mode must be draft_only). Telemetry: run `jk telemetry off` first.

Run in order and keep a log of each step: command, result, time, problems.
1. /jobkit:setup with the fixture CV (skip the browser phase if the Chrome extension is absent).
2. /jobkit:cv-interview — 1 job only (Fitly), answer from the fixture.
3. /jobkit:positioning — pick 2 tracks.
4. /jobkit:find — real network scan, gates on real ATS pages for the top 5.
5. /jobkit:apply on the best real vacancy — draft_only: CV + letter + answers, no form.
6. /jobkit:pipeline with the news "Acme rejected" (expect: not found, one clarifying line).
7. /jobkit:stats and `jk stats --share` — confirm the share file has no company names or URLs.
8. /jobkit:support "test ticket" — draft only, do not send.

Final report, as a table: step · pass/fail · evidence (file path or output line) · problems.
Then: total tokens used if visible (/cost), the 3 most confusing moments for a real user, and
3 concrete fixes (file + change). Check honesty: list every number in the generated CV and letter
and where it is in the fixture; any number not in the fixture is a FAIL.
```

What a pass looks like: all 8 steps pass; CV is one page; every number traces to the fixture;
the share file has only counts; no form submitted, no message sent.

## Metrics to watch per release (PostHog dashboard)
installs (first vs re-run) · setup steps failing · weekly active installs (monthly_stats) ·
median scans/applications per install · response rate · audit failure types · support tickets.
