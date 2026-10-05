---
name: Setup on a fictional persona, no human
tags: [setup, smoke]
runs: 1
max_turns: 40
timeout_seconds: 900
---
/jobkit:setup tests/fixtures/persona/cv.md

You are in test mode. Do not ask me anything: take every answer from tests/fixtures/persona/answers.md.
Skip the browser phase. Skip `jk boards` and the scan (no network in tests). At the end print
exactly one line: SETUP-DONE <number of TODO left in me/profile.yaml>.
