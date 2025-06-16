from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Pattern

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    yaml = None

logger = logging.getLogger(__name__)

CATEGORY_ORDER = [
    ("OBS", "Нечинний"),
    ("BUD", "Бюджет"),
    ("SCI", "Науковець"),
    ("INS", "Інститут"),
    ("REG", "Регулювання"),
    ("STA", "Статус"),
    ("BAS", "базис ННТД"),
    ("HOM", "Омонім"),
]


def _simple_yaml_load(path: Path) -> Dict[str, List[str]]:
    data: Dict[str, List[str]] = {}
    key: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            key = line.rstrip(":").strip()
            data[key] = []
        elif key is not None and line.lstrip().startswith("-"):
            item = line.split("-", 1)[1].strip().strip('"')
            item = item.replace("\\\\", "\\")
            data[key].append(item)
    return data


class RuleEngine:
    def __init__(self, terms_path: Path) -> None:
        if yaml:
            data = yaml.safe_load(terms_path.read_text(encoding="utf-8"))
        else:  # pragma: no cover - fallback when PyYAML missing
            data = _simple_yaml_load(terms_path)
        self.triggers: Dict[str, List[Pattern[str]]] = {
            key: [re.compile(p) for p in val] for key, val in data.items()
        }

    def match(self, text: str) -> (str, List[str]):
        found_terms: List[str] = []
        lowered = text.lower()
        if re.search(r"втратив чинн|скасован", lowered):
            return "OBS", ["втратив чинність"]
        if "нечинна однорідність" in lowered:
            return "OBS", ["нечинна однорідність"]

        for code, name in CATEGORY_ORDER[1:]:
            patterns = self.triggers.get(name, [])
            for pat in patterns:
                if pat.search(text):
                    found_terms.append(pat.pattern)
                    return code, found_terms
        hom_patterns = self.triggers.get("Омонім", [])
        if any(p.search(text) for p in hom_patterns):
            return "HOM", [p.pattern for p in hom_patterns if p.search(text)]
        return "UNLABELLED", []
