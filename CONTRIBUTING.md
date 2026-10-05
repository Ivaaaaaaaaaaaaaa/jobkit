# Contributing to jobkit

Users get the agent rules from `skills/jobkit/SKILL.md`; this file is for working on the kit.
- Layout: `.claude-plugin/` manifests · `skills/jobkit/SKILL.md` core rules (lazy-loaded) · `commands/`
  slash commands · `playbooks/` on-demand detail · `scripts/` (`jk.py` is the single entry) ·
  `templates/` me/ blanks · `config/` seed boards + telemetry endpoint · `hooks/` prompt hook ·
  `evals/` agent evals · `tests/fixtures/` fictional persona.
- Token budget: SKILL.md ≤ 1.5k tokens, each command ≤ 500, agent-facing text in English, script
  output compact. Measure before/after a change.
- Before a release: `python3 scripts/jk.py test` green; bump `VERSION`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json` together (CI checks); add a CHANGELOG entry.
- Never commit real personal data. Fixtures are fictional.
