# Contact instead of a form, follow-ups, networking

Messages as the candidate are sent by the candidate; the agent prepares everything so one action
remains (exception: `autonomy.send_messages: true` + explicit request for those messages).

## 1. Look for a real form first
Company careers/ATS → same role with a form? Then it's a normal application; the message is extra.
Hiring manager's LinkedIn → recent posts → job link.

## 2. Telegram kit (exactly four things, in order)
1. Clickable link to the person: `https://t.me/<handle>`.
2. Vacancy link.
3. Tailored CV as PDF: path + reveal the file (`open -R <path>`) for one drag.
4. Message, 5–7 lines (in the vacancy's language):
```
Hi! Applying for <role> — <link>.
Currently <role> at <company>: <one result with a number>.
<One line covering the role's main requirement>.
CV attached, happy to have a call.
<Name>, <phone>
```

## 3. LinkedIn
Message to recruiter/hiring manager: 3–5 lines, same skeleton, CV attached. Invitation note
(≤200 chars): "Hi <name>, applied for <role> at <company> — <one number about you>. Would love to
connect." Free personalized invites are scarce — spend on hiring managers. No Premium without the candidate.

## 4. Email
Subject "<Role> — <Name>"; 5–8 lines; CV attached. Draft in the candidate's mailbox (if connected) or as text.

## 5. Follow-ups
| When | What |
|---|---|
| 7 days of silence after applying | short LinkedIn note: applied, one number, status? |
| day after an interview | thanks + one idea from the talk + what else you can show |
| after rejection | thanks, one-line feedback request, stay in touch |
| promised date passed | polite check after 2 working days |
`jk t due` lists them; afterwards `jk t set <id> <status> "follow-up sent" --next … --date …`.

## 6. Referrals
Convert far better than cold. Weekly: "anyone you know at companies in the queue?" Draft per contact:
role, link, why you fit (2 lines), CV.
