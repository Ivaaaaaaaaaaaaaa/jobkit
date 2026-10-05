# Forms — mechanics and engine traps

Found an engine where the tool reports success but the field is empty → add a section here.

## 0. Browser
Load once per batch:
`ToolSearch select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__javascript_tool`
No `file_upload` → don't start (can't attach CV). A built-in browser without the user's logins/file_upload
is fine for reading postings, not for forms.

## 1. One role
1. `tabs_create_mcp` → `navigate` to the form. One role = one tab.
2. Map the form (`read_page`/`find`). Answer key yes/no fields (work rights, contractor), map AGAIN —
   conditional fields render only after answers.
3. CV first if the engine re-renders after upload (Ashby, Rippling).
4. Fields in order; after each read the value via JS (`document.querySelector('[name="…"]').value`).
5. Free text from answers.md (audited).
6. Consent boxes of the application itself (GDPR/privacy) — tick. Cookie banner — reject non-essential.
   Marketing opt-ins — no.
7. `jk formcheck` → paste into `javascript_tool` → result in the report.
8. Leave the tab on the final screen.

## 2. Typing traps
- Background tab loses keystrokes, yet `computer type` says "Typed". Make the tab active; check
  `document.visibilityState === 'visible'`.
- JS `el.focus()` doesn't deliver typing — focus by clicking.
- Long text → `form_input` by ref (`type` drops ~1 char per 40–60). Verify by reading `value`.
- Typing into a filled field appends → `cmd+a`, `Delete` first.
- Ten `type` calls in a row lose values silently — one field, then read.
- Reading tools work on background tabs.

## 3. CV upload
JS-click the upload button (creates hidden `input[type=file]`) → `find` "file" → `file_upload` with
tabId, ref, ABSOLUTE path. Proof: file name visible. ~10 MB limit. PDF asked → `jk cv … --pdf`.

## 4. Engines
- **Greenhouse:** text via `form_input`; React dropdowns need click → type → pick. City: pick the
  autocomplete suggestion. School: directory search; not listed → "Other". reCAPTCHA often → stop.
  formcheck accurate. No drafts.
- **Ashby:** CV first (refs shift after upload). `form_input`/ref clicks often "succeed" without
  reaching form state → coordinate click + real typing, read value each time. Yes/No toggles are
  `button[aria-pressed]` (formcheck can't see them). Final proof = Submit response (lists missing
  fields); one re-fill pass is normal — warn the candidate in confirm_each mode. No drafts.
- **Lever:** simple one page, `form_input` works; form at `…/apply`.
- **Workable:** multi-step; go to the last step.
- **Teamtailor:** second application to the same company → email verification link
  (`…/email_verification_needed`); the candidate (or agent with mailbox access) opens it.
- **Recruitee, Personio, SmartRecruiters, BambooHR:** ordinary; BambooHR may have captcha.
- **Rippling:** CV first, it pre-fills contacts. formcheck false-green → verify by JS dump. Upload
  proof: "File … uploaded successfully".
- **iframe forms (Comeet etc.):** click Apply, take the frame `src`, `location.href = src`.
- **Workday, SuccessFactors, Taleo, iCIMS with sign-up:** account required → stop, report.
- **LinkedIn Easy Apply** (candidate's Chrome): modal may need a second click after 6–8 s; refs often
  fail inside → coordinates, note it. Long text via `form_input` by ref. Dates only via the picker.
  Upload the tailored CV, not a saved generic one. Drafts exist (X → Save).

## 5. Workaround ladder (record failed steps before giving up)
ref path → coordinates where ref fails → iframe `src` in own tab → login wall: public board JSON
(`api.ashbyhq.com/posting-api/job-board/<org>`, `boards-api.greenhouse.io/v1/boards/<org>/jobs`,
`api.lever.co/v0/postings/<org>?mode=json`) or company careers page → dead link: find it on the
company site. Beyond that only the five stops.

## 6. Ready and after
Ready: all wizard steps done, CV attached and visible, formcheck OK (Ashby caveat), tab alive.
After sending: "thank you" screen, close tabs one by one, `jk t set <id> applied`.
