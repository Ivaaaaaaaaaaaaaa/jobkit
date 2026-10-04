#!/usr/bin/env python3
"""Проверка, что всё готово к работе. Печатает ✅ / ⚠ / ✗ и что сделать.

    python scripts/doctor.py          # окружение + заполненность me/
    python scripts/doctor.py --test   # плюс самотесты всех скриптов (без сети)
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ME = ROOT / "me"
bad = 0


def ok(msg):
    print(f"✅ {msg}")


def warn(msg):
    print(f"⚠  {msg}")


def fail(msg):
    global bad
    bad += 1
    print(f"✗  {msg}")


def main() -> int:
    print(f"Папка: {ROOT}\n")
    if sys.version_info >= (3, 10):
        ok(f"Python {sys.version.split()[0]}")
    else:
        fail(f"Python {sys.version.split()[0]} — нужен 3.10+")
    for mod, pkg in (("yaml", "pyyaml"), ("docx", "python-docx")):
        if importlib.util.find_spec(mod):
            ok(f"пакет {pkg}")
        else:
            fail(f"нет пакета {pkg}: pip install -r requirements.txt")
    if shutil.which("soffice") or Path("/Applications/LibreOffice.app").exists():
        ok("LibreOffice — PDF из DOCX собирается")
    else:
        warn("нет LibreOffice — PDF не соберётся (brew install --cask libreoffice). DOCX работает.")

    print()
    files = {
        "profile.yaml": "контакты, цели, фильтры — /onboard",
        "experience-bank.md": "факты о себе — /cv-interview",
        "positioning.md": "треки позиционирования — /positioning",
        "application-answers.md": "ответы на типовые поля анкет — /onboard",
        "cv/base.yaml": "данные резюме — /cv-interview",
    }
    for f, how in files.items():
        p = ME / f
        if not p.exists():
            fail(f"me/{f} нет — {how}")
            continue
        text = p.read_text(encoding="utf-8")
        todo = len(re.findall(r"TODO|<заполнить>|\?\?\?", text))
        if todo:
            warn(f"me/{f}: осталось незаполненных мест — {todo} ({how})")
        else:
            ok(f"me/{f}")

    if (ME / "profile.yaml").exists() and importlib.util.find_spec("yaml"):
        import yaml
        p = yaml.safe_load((ME / "profile.yaml").read_text(encoding="utf-8")) or {}
        if not (p.get("search") or {}).get("title_include"):
            fail("profile.yaml: search.title_include пуст — поиск не знает, какие роли брать")
        email = (p.get("contacts") or {}).get("email", "")
        if email and not re.match(r"[^@\s]+@[^@\s]+\.\w+$", email):
            fail(f"profile.yaml: email «{email}» выглядит неверно")

    orgs = ROOT / "config" / "ats_orgs.txt"
    n = sum(1 for l in orgs.read_text().splitlines() if l.strip() and not l.startswith("#")) if orgs.exists() else 0
    (ok if n else warn)(f"config/ats_orgs.txt: компаний в обходе — {n}")

    gi = (ROOT / ".gitignore").read_text() if (ROOT / ".gitignore").exists() else ""
    if "me/" in gi and "data/" in gi:
        ok(".gitignore закрывает me/ и data/ — личное не уедет в git")
    else:
        fail(".gitignore не закрывает me/ и data/ — личные данные могут уехать в git")

    if "--test" in sys.argv:
        print()
        for s in ("tracker.py", "render_cv.py", "text_audit.py"):
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / s), "--selftest"],
                               capture_output=True, text=True)
            (ok if r.returncode == 0 else fail)(f"{s}: {(r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else r.returncode}")

    print("\nИтог: " + ("всё готово" if not bad else f"проблем {bad} — исправь ✗ сверху"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
