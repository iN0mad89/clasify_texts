from __future__ import annotations

import logging
from pathlib import Path
from typing import List

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Document = None

try:
    from pdfminer.high_level import extract_text  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    extract_text = None

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


def read_file(path: Path) -> str:
    if not path.exists():
        raise ParseError(f"Файл не знайдено: {path}")
    try:
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".docx":
            if Document is None:
                raise ParseError("python-docx не встановлено")
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        if path.suffix.lower() == ".pdf":
            if extract_text is None:
                raise ParseError("pdfminer-six не встановлено")
            return extract_text(str(path))
    except Exception as exc:  # pragma: no cover - logging
        logger.error("Помилка читання %s: %s", path, exc)
        raise ParseError(str(exc))
    raise ParseError(f"Непідтримуваний формат: {path.suffix}")


def find_files(folder: Path, patterns: List[str]) -> List[Path]:
    files: List[Path] = []
    for pattern in patterns:
        files.extend(folder.rglob(pattern))
    return files
