---
description: Install and onboard — tools check, CV + LinkedIn import, profile, geo, boards fit, first scan
argument-hint: "[optional: path to CV or LinkedIn PDF]"
---
Rules: skill jobkit (load it if not loaded). `jk` = `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jk.py"`. Playbooks: `${CLAUDE_PLUGIN_ROOT}/playbooks/`.
Input: $ARGUMENTS. Resumable: skip finished phases (see `data/setup-state.json` and TODOs in me/).
Script: playbooks/onboarding.md. Talk in the user's language, one phase at a time, 3–6 questions max,
AskUserQuestion for choices. Edit me/ files in place (keep template comments).

0. **How it works (first run only).** Show the scheme and "What the agent does / never does" from
   `${CLAUDE_PLUGIN_ROOT}/GUIDE.md` in the user's language, 10 lines max, then one line: "about 30–60
   minutes, you can stop any time and continue later". Don't wait for an answer — go on.
1. **Machine.** `jk setup` → fix FAIL lines (offer commands, run after OK). Explain where data lives.
   Mention once: anonymous usage stats (install ping, monthly counts, no personal data) are on;
   `jk telemetry off` disables. Respect a "no".
2. **Browser.** Check Claude in Chrome tools (ToolSearch `claude-in-chrome`). Missing → install steps
   (playbooks/onboarding.md §Browser). Without it: everything except forms works.
3. **Import.** Ask for CV (PDF/DOCX) and LinkedIn PDF (Profile → More → Save to PDF).
   `jk import <file> [--as linkedin]` → read data/import/*.txt once → fill `me/experience-bank.md`
   and `me/cv/base.yaml`; numbers marked "from CV, verify". Old applications → `jk t add ... --status applied`.
4. **Profile.** Phases 2–4 of the onboarding script: target roles & level → title_include/exclude;
   geo, work authorization, salary (+ three tiers in application-answers §3); contacts; autonomy,
   skip_companies, banned_claims. Show what you wrote after each phase.
5. **Boards.** `jk boards` → show kept/dropped and top companies; ask for companies to add (# mine).
6. **First scan.** `jk scan --top 10` → show; offer /jobkit:cv-interview (stronger CV), then /jobkit:positioning, then /jobkit:find.
7. `jk setup --check`, then `jk setup --phase done`.
8. **Daily routine.** Show "Каждый день" and "Ситуации" from GUIDE.md (in the user's language) and
   where the full guide is: `${CLAUDE_PLUGIN_ROOT}/GUIDE.md`. Offer to copy it into the folder
   (`cp` → `./GUIDE.md`) so it's at hand.

After each phase run `jk setup --phase <machine|browser|import|profile|boards|first_scan>`; a phase
the user skips → `--skip`; a phase that failed → `--fail <short_code>` (a code like
`no_chrome_extension`, never personal data). This keeps the resume point and the onboarding funnel.
