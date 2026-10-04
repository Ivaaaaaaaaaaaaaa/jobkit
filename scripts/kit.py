"""Общее для скриптов: профиль, HTTP, фильтры по названию роли и по гео.

Все пороги и ключевые слова живут в me/profile.yaml, а не в коде, — поэтому один и тот же
код работает для продакта, аналитика или дизайнера: меняется только профиль.
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ME = ROOT / "me"
DATA = ROOT / "data"
PROFILE = ME / "profile.yaml"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/126 job-search-kit", "Accept": "application/json"}
_CTX = ssl.create_default_context()


def load_profile() -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("Нет pyyaml. Поставь: pip install -r requirements.txt")
    if not PROFILE.exists():
        sys.exit("Нет me/profile.yaml. Запусти в Claude Code команду /onboard.")
    return yaml.safe_load(PROFILE.read_text(encoding="utf-8")) or {}


def get(url: str, timeout: int = 15, data: bytes | None = None, headers: dict | None = None) -> str | None:
    try:
        req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
            return r.read(8_000_000).decode("utf-8", "replace")
    except Exception:
        return None


def get_json(url: str, **kw):
    body = get(url, **kw)
    try:
        return json.loads(body) if body else None
    except ValueError:
        return None


def age_days(value) -> float | None:
    """Возраст публикации в днях; принимает ISO-строку, секунды или миллисекунды."""
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            v = float(value)
            d = datetime.fromtimestamp(v / 1000 if v > 1e11 else v, timezone.utc)
        else:
            d = datetime.fromisoformat(str(value).replace("Z", "+00:00").replace(" UTC", ""))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc) - d).total_seconds() / 86400, 1)
    except Exception:
        return None


def _rx(words: list[str]) -> re.Pattern | None:
    words = [w.strip() for w in (words or []) if w and w.strip()]
    if not words:
        return None
    return re.compile("|".join(rf"\b{re.escape(w)}\b" if w.isalnum() else re.escape(w) for w in words), re.I)


class Gates:
    """Фильтры из профиля. Решают «стоит ли открывать», а не «подаваться ли»."""

    def __init__(self, profile: dict):
        s = profile.get("search", {}) or {}
        g = profile.get("geo", {}) or {}
        self.title_ok = _rx(s.get("title_include", []))
        self.title_bad = _rx(s.get("title_exclude", []))
        self.geo_ok = _rx(g.get("ok_keywords", []))
        self.geo_bad = _rx(g.get("block_keywords", []))
        self.max_age = float(s.get("max_age_days", 14))
        self.skip_companies = {c.lower() for c in profile.get("skip_companies", []) or []}

    def title(self, title: str) -> bool:
        if self.title_bad and self.title_bad.search(title or ""):
            return False
        return bool(self.title_ok.search(title or "")) if self.title_ok else True

    def geo(self, location: str) -> str:
        """wide — подходит; blocked — точно мимо; check — открыть и прочитать."""
        loc = location or ""
        oks = {m.group(0).lower() for m in self.geo_ok.finditer(loc)} if self.geo_ok else set()
        bad = bool(self.geo_bad and self.geo_bad.search(loc))
        # «Remote» — слабый сигнал: «Remote - US» и «New York (Remote)» — это США.
        # Стоп-регион перебивает голое «remote»; перебить его может только сильное
        # слово («Europe», «EMEA», «worldwide»), и тогда — открыть и прочитать.
        strong = oks - {"remote", "hybrid", "remote-first"}
        if bad:
            return "check" if strong else "blocked"
        if oks:
            return "wide"
        return "check"

    def fresh(self, days: float | None) -> bool:
        return days is None or days <= self.max_age

    def company(self, name: str) -> bool:
        return (name or "").lower() not in self.skip_companies


def tracker_rows() -> list[dict]:
    sys.path.insert(0, str(Path(__file__).parent))
    import tracker
    return tracker.load()


def known(rows: list[dict], company: str, role: str, url: str) -> str:
    import tracker
    return tracker.check(rows, company, role, url)[0]
