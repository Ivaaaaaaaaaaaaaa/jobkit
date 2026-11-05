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
- **Screenshot the tab before typing and before Submit** — it makes the tab active. A background tab
  loses keystrokes, yet `computer type` says "Typed". Check `document.visibilityState === 'visible'`.
- JS `el.focus()` doesn't deliver typing — focus by clicking.
- Long text → `form_input` by ref (`type` drops ~1 char per 40–60). Verify by reading `value`.
- Typing into a filled field appends → `cmd+a`, `Delete` first.
- Ten `type` calls in a row lose values silently — one field, then read.
- Reading tools work on background tabs.

## 2b. Background tab — when the tab can't be made visible
Happens when the Chrome window is hidden, the Mac sleeps, or another agent drives the active tab.
Coordinates and keyboard then go nowhere or into someone else's tab. JS works. Ladder, one field per call:
1. **Text, React forms (Ashby and most others):** `el.scrollIntoView(); el.click(); el.focus();`
   `el.select(); document.execCommand('delete'); document.execCommand('insertText', false, '<text>');`
   then `el.dispatchEvent(new FocusEvent('focusout', {bubbles: true}))`. The form takes it as real
   typing. A batch of insertText calls in one go loses fields — one field, pause ~300 ms, read back.
2. **Plain inputs:** native setter + events:
   `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, v);`
   `el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true}))`
   (`HTMLTextAreaElement.prototype` for textareas).
3. **Toggles / custom buttons (Yes/No):** a lone `.click()` paints the button but the form state
   stays empty. Send the full chain `pointerdown → mousedown → pointerup → mouseup → click`, first on
   the opposite option, then on the one you want. Still empty → `scroll_to` the ref, then click by ref.
4. **Comboboxes:** set the input value (step 2), then click `[role=option]` with the same chain.
   Greenhouse react-select whose menu opens and closes at once: walk from `input.select__input` up the
   `__reactFiber…` chain to a `stateNode` with `selectOption`, call
   `selectOption(props.options.find(o => o.label === '<answer>'))`.
5. **Timers don't run in hidden tabs.** `setTimeout` inside one call can hang it for ~45 s. Split into
   separate calls instead: call 1 opens the list, call 2 reads and clicks the option.
6. **Submit:** JS `.click()` on the submit button, or by ref after `scroll_to`. Proof = the success
   text on the page ("successfully submitted", "Thank you", "You have successfully applied"), never
   the tool's own report.

## 3. CV upload
JS-click the upload button (creates hidden `input[type=file]`) → `find` "file" → `file_upload` with
tabId, ref, ABSOLUTE path. Proof: file name visible. ~10 MB limit. PDF asked → `jk cv … --pdf`.

## 4. Engines
- **Greenhouse:** text via `form_input`; React dropdowns need click → type → pick. In a background
  tab: `scroll_to` the ref first, then click by ref, pick the option by ref from `find`; menu that
  closes at once → `selectOption` (§2b.4). City: pick the autocomplete suggestion. School: directory
  search; not listed → "Other" (the school list per board is small; check with
  `boards.greenhouse.io/v1/boards/<org>/education/schools?term=…`). reCAPTCHA often → stop.
  formcheck accurate. No drafts.
- **Ashby:** CV first (refs shift after upload). `form_input`/ref clicks often "succeed" without
  reaching form state → coordinate click + real typing, read value each time; background tab →
  insertText per field (§2b.1). Yes/No toggles are `button[aria-pressed]` (formcheck can't see them):
  click by ref after `scroll_to`. A "Yes" can add conditional fields (visa, city) — map again.
  Final proof = Submit response (lists missing fields); one re-fill pass of the named fields is
  normal — warn the candidate in confirm_each mode. No drafts.
- **Lever:** form at `…/apply`. `find` and full `read_page` may fail ("Page script returned empty
  result") and the interactive tree stops after email. CV: `file_upload` on the nearest ref after
  "ATTACH RESUME". Other fields: native setter by `name`; radios/checkboxes `.click()`. Invisible
  hCaptcha usually lets Submit through. Lever may need a second Submit click.
- **Workable:** multi-step; go to the last step.
- **Teamtailor:** second application to the same company → email verification link
  (`…/email_verification_needed`); the candidate (or agent with mailbox access) opens it.
- **Breezy:** parses the uploaded CV into Experience/Education by itself — check every row
  (wrong titles, empty companies, extra rows; delete extras with the block's "Delete").
- **Recruitee, Personio, SmartRecruiters, BambooHR:** ordinary; BambooHR may have captcha.
- **Rippling:** CV first, it pre-fills contacts. formcheck false-green → verify by JS dump. Upload
  proof: "File … uploaded successfully". Background tab: dropdown = two calls without timers (§2b.5).
- **Gem:** labels aren't `<label>`, so formcheck says "required: 0" (false green) — verify by JS dump
  of `input[type=text]`, `textarea` values and `input[type=radio]:checked`. Radios: coordinate click.
  At the bottom pick **"Apply without saving"** ("Apply and save" creates a Gem account).
- **JOIN (join.com):** step wizard (email → CV → personal → links → letter → review → "Confirm &
  apply"); coordinate clicks and real typing. CV and letter **PDF only** — DOCX silently fails
  (`jk cv … --pdf`). After "Confirm & apply" comes "Verify your email address": not sent until the
  link from noreply@join.com is opened.
- **HR-Manager / Talentech:** one ASP.NET page, plain `value` works. Documents: pick the category
  (CV / Cover letter) in the dropdown first, then `file_upload`; each file becomes a row. Labels
  aren't `<label>` — take the question from the text above the field. No password: the service
  creates a candidate profile itself and emails a login.
- **Forms on the company's own site (Gravity Forms, WordPress, custom):** the first `<form>` on the
  page is often the site search — formcheck picks the largest form, still check its `form` field in
  the result. Gravity Forms: required = `.gfield_contains_required`; dates `YYYY-mm-dd`; files via the
  hidden plupload inputs. Send button may need a JS click.
- **iframe forms (Comeet etc.):** click Apply, take the frame `src`, `location.href = src`.
- **Workday, SuccessFactors, Taleo, iCIMS with sign-up:** account required → stop, report.
- **LinkedIn Easy Apply** (candidate's Chrome): modal may need a second click after 6–8 s; refs often
  fail inside → coordinates, note it. Long text via `form_input` by ref. Dates only via the picker.
  Upload the tailored CV, not a saved generic one: the upload button lives in shadow DOM and
  `file_upload` refuses it — JS-click the button found by walking every `shadowRoot`, the modal then
  creates a hidden `input[type=file]`; `find` "file input" → ref → `file_upload`. Consent checkbox:
  `form_input` looks ticked but "Review" says required → coordinate click. Number fields (salary)
  take digits only, no ranges. The email is the LinkedIn account's (can't pick the job-search one).
  Drafts exist (X → Save).

## 5. Workaround ladder (record failed steps before giving up)
ref path → coordinates where ref fails → background-tab JS (§2b) → iframe `src` in own tab →
login wall: public board JSON
(`api.ashbyhq.com/posting-api/job-board/<org>`, `boards-api.greenhouse.io/v1/boards/<org>/jobs`,
`api.lever.co/v0/postings/<org>?mode=json`) or company careers page → dead link: find it on the
company site. Beyond that only the five stops.

## 6. Ready and after
Ready: all wizard steps done, CV attached and visible, formcheck OK (Ashby caveat), tab alive.
After sending: "thank you" screen, close tabs one by one, `jk t set <id> applied`.
