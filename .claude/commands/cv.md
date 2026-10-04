---
description: Собрать CV — базовое, вариант под трек или под конкретную вакансию (DOCX/PDF)
argument-hint: "[пусто — базовое | имя трека | ссылка на вакансию или id]"
---

Собери резюме по `playbooks/cv-guide.md`. Запрос: $ARGUMENTS

- Пусто → базовое: `python3 scripts/render_cv.py --pdf`.
- Трек из `me/positioning.md` → `me/cv/variant-<трек>.yaml` (создай, если нет) → рендер.
- Вакансия → `data/applications/<id>/cv.yaml` под JD (тайтл, саммари с 3–5 словами из JD, порядок
  буллетов и навыков) → рендер.

Перед рендером — `text_audit.py --kind summary` по саммари. После — проверь длину (≤ 1 страницы),
открой и посмотри файл, покажи путь кандидату. Факты только из `me/experience-bank.md`.
