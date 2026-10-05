# Changelog

## 0.2.0 — 2026-10-05
- Packaged as a Claude Code plugin (marketplace install, `/jobkit:*` commands, lazy skill instead of CLAUDE.md).
- `jk` single CLI; `jk setup` installs its own venv, folders, permissions; idempotent.
- CV/LinkedIn import (`jk import`), board fitting to profile and geo (`jk boards`).
- Local metrics (`jk stats`), anonymous telemetry (install, monthly snapshot), support tickets.
- Agent-facing text in compact English (~3× fewer tokens); geo gate: "Remote - US" no longer passes.
- Offline e2e test on a fictional persona; CI; agent evals.

## 0.1.0 — 2026-10-04
- First version: rules, playbooks, tracker, scan, CV renderer, text audit.
