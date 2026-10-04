#!/usr/bin/env python3
"""Проверка текста перед отправкой: CV-саммари, письмо, ответ анкеты.

Ловит то, что модель делает чаще всего и что дороже всего стоит на подаче:
    • цифра, которой нет в me/experience-bank.md        -> выдуманная метрика
    • запрещённое утверждение из profile.yaml -> banned_claims (навык, которого нет)
    • «you / your team / вы» в саммари CV                -> саммари пишется о себе
    • эмодзи, «I am excited / passionate / thrilled»     -> шаблонный тон
    • плейсхолдеры [Company], <роль>, TODO, XXX          -> недописанный шаблон
    • длина вне рамок для письма
Скрипт не заменяет чтение глазами — он не пропускает брак.

Запуск:
    python scripts/text_audit.py --text "текст" [--kind summary|letter|answer] [--company Acme]
    python scripts/text_audit.py --file data/applications/<id>/letter.md --kind letter --company Acme
    python scripts/text_audit.py --selftest
Exit 0 — ok, 1 — есть проблемы.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "me" / "experience-bank.md"
PROFILE = ROOT / "me" / "profile.yaml"

CLICHES = r"\b(i am (so )?(excited|thrilled|passionate)|i'?m (so )?(excited|thrilled)|dream (job|company)" \
          r"|perfect fit|hit the ground running|synergy|rockstar|ninja|guru|results-driven|team player)\b"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
PLACEHOLDER = re.compile(r"\[[A-Z][^\]]{1,30}\]|<[a-zа-я_ ]{2,30}>|\bTODO\b|\bXXX\b|\bTBD\b", re.I)
SECOND_PERSON = re.compile(r"\b(you|your|you're|yours)\b|\b(вы|вас|вам|ваш\w*)\b", re.I)
NUM = re.compile(r"(?<![\w.])[~≈+\-−]?\$?€?£?\d[\d,.]*\s?(%|k|K|M|x|×)?")


def numbers(text: str) -> set[str]:
    out = set()
    for m in NUM.finditer(text):
        n = re.sub(r"[~≈+\-−$€£,\s]", "", m.group(0)).lower().replace("×", "x")
        if n and not re.fullmatch(r"(19|20)\d\d", n) and n not in {"1", "2", "3", "0"}:
            out.add(n)
    return out


def banned_claims() -> list[str]:
    if not PROFILE.exists():
        return []
    try:
        import yaml
        return [b for b in (yaml.safe_load(PROFILE.read_text(encoding="utf-8")) or {}).get("banned_claims") or [] if b]
    except Exception:
        return []


def audit(text: str, kind: str = "answer", company: str = "", bank: str | None = None,
          banned: list[str] | None = None) -> list[str]:
    bank = bank if bank is not None else (BANK.read_text(encoding="utf-8") if BANK.exists() else "")
    banned = banned if banned is not None else banned_claims()
    probs = []
    if bank:
        unknown = sorted(numbers(text) - numbers(bank))
        if unknown:
            probs.append(f"цифры не из experience-bank: {', '.join(unknown)} — убери или сперва внеси факт в банк")
    for b in banned:
        if re.search(rf"\b{re.escape(b)}\b", text, re.I):
            probs.append(f"запрещённое утверждение «{b}» (profile.yaml -> banned_claims)")
    if EMOJI.search(text):
        probs.append("эмодзи")
    if re.search(CLICHES, text, re.I):
        probs.append(f"штамп: «{re.search(CLICHES, text, re.I).group(0)}»")
    if PLACEHOLDER.search(text):
        probs.append(f"плейсхолдер: «{PLACEHOLDER.search(text).group(0)}»")
    if kind == "summary" and SECOND_PERSON.search(text):
        probs.append("саммари обращается к работодателю («you/your») — пиши о своём опыте")
    words = len(text.split())
    if kind == "letter":
        if not 90 <= words <= 300:
            probs.append(f"письмо {words} слов — держи 120–260")
        if company and company.lower() not in text.lower():
            probs.append(f"в письме не названа компания «{company}»")
    if kind == "summary" and words > 90:
        probs.append(f"саммари {words} слов — держи 3–4 предложения, до ~80 слов")
    return probs


def selftest() -> int:
    bank = "Grew retention +30% in 2024. Shipped 5 launches. Cut cost by 40%."
    assert audit("Grew retention 30% and cut cost 40%.", bank=bank, banned=[]) == []
    assert any("цифры" in p for p in audit("Grew revenue 250%.", bank=bank, banned=[]))
    assert any("RAG" in p for p in audit("Built RAG systems.", bank=bank, banned=["RAG"]))
    assert any("саммари" in p for p in audit("You need a PM who ships.", kind="summary", bank=bank, banned=[]))
    assert any("компания" in p for p in audit("word " * 150, kind="letter", company="Acme", bank=bank, banned=[]))
    assert any("плейсхолдер" in p for p in audit("Hello [Company] team", bank=bank, banned=[]))
    print("text_audit selftest: ok")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--kind", default="answer", choices=["summary", "letter", "answer"])
    ap.add_argument("--company", default="")
    a = ap.parse_args()
    text = a.text or (Path(a.file).read_text(encoding="utf-8") if a.file else sys.stdin.read())
    probs = audit(text, a.kind, a.company)
    if not BANK.exists():
        print("⚠ нет me/experience-bank.md — цифры не сверены")
    for p in probs:
        print(f"✗ {p}")
    print("ok" if not probs else f"\nпроблем: {len(probs)}")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
