# Experience interview — question bank (used by /jobkit:cv-interview)

People remember tasks ("did onboarding"), not results ("onboarding converts 12 pp better").
Turn the first into the second. Ask in the user's language; write the bank/CV in `docs_language`.

## Rules
- One job at a time, newest first. Last 2–3 jobs in depth; older than 5 years — one line.
- Each answer → draft bullet "result → how → tools", show it.
- Never suggest numbers. No number → section E, mark "≈".
- "We did" → "what did *you* do? would it have happened without you?"

## A. Context
1. What does the company do, for whom; users/clients/revenue roughly?
2. Stage (pre-revenue / growing / corporate); headcount overall and in product?
3. Which product or part was yours; who were the users?
4. Daily team: how many devs, designers, analysts; who did you report to?
5. Official title; what the role was in substance (→ `title_options`, honest only).
6. Why joined, why left (interview only, not CV).

## B. Achievements (start open: "what are you proudest of here?")
- **Launches:** what did you ship from scratch; how many use it; time idea→launch vs usual?
- **Product metrics:** which did you move (conversion, retention, activation, revenue, ARPU, NPS,
  time-on-task); before/after even roughly; over what period and audience?
- **Money/efficiency:** revenue or savings; hours/people/costs saved; what did you automate?
- **Decisions:** what did you decide NOT to do and were right; what did you kill; a data-backed disagreement?
- **Discovery:** how many user interviews; what came out; research/usability tests that changed things?
- **Experiments:** how many A/B tests; best win; the failure that taught most?
- **People/process:** hired, onboarded, mentored whom; process you built or fixed; vendors/budget?
- **Complexity:** hardest technical or org thing you pushed through; integrations, platform, compliance?

## C. Tools and methods
Analytics (Amplitude/Mixpanel/GA/SQL/Excel — hands-on or dashboards?), design/prototyping (Figma,
no-code, code with AI tools), delivery (Jira/Linear/Notion), methods actually used (CJM, JTBD, RICE,
OKR, unit economics), AI at work (concrete: "built X, saves Y"). Level: "do myself" / "understand
and direct" / "heard of" — only the first two go to the CV.

## D. STAR stories (6–8): Situation → Task → Action → Result with a number
Launch · failure · conflict · prioritization · influence without authority · data changed my mind ·
ambiguity · hardest customer.

## E. No number — honest estimate
"How many people saw it per day/month?" (base) · "more like +5% or +50%?" (order) · "hours per week
before vs after?" (savings) · "what would a contractor charge?" (money) · "where can it be checked —
dashboard, report, email?". Write "≈30%" and note in the bank how it was estimated; no method → no number.

## F. Junior / career switch
Previous profession (analyst, QA, marketing, support, dev, PM-adjacent): which product decisions
did you make or influence? Pet projects (users, learnings), courses with full cases, internships,
hackathons, freelance — with results. Product work without the title: who decided what to build and
collected feedback?

## G. CV variants to propose
| Variant | When | Changes |
|---|---|---|
| Base | default | track A title, balanced bullets |
| Per track (`me/cv/variant-<track>.yaml`) | that track's roles | title, summary, lead bullets, skill order |
| One page | always if < 10 yrs | last 4–5 yrs, ≤4 bullets per role |
| Two pages | only if "full history" asked | everything |
| Other language | local companies/recruiters | translation + local terms |
| Per vacancy | every application | `data/applications/<id>/cv.yaml` |
