from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Pattern

import yaml

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


class RuleEngine:
    def __init__(self, terms_path: Path) -> None:
        data = yaml.safe_load(terms_path.read_text(encoding="utf-8"))
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
