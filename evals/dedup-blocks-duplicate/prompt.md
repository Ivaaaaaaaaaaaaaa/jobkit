---
name: Agent does not apply twice to the same role
tags: [dedup]
runs: 3
max_turns: 15
---
Fixture setup: `JK_TELEMETRY_OFF=1 python3 scripts/jk.py setup`, then
`python3 scripts/jk.py t add --company Acme --role "Growth PM" --url https://jobs.lever.co/acme/1 --status applied`.
Then: /jobkit:apply https://jobs.lever.co/acme/1/apply
