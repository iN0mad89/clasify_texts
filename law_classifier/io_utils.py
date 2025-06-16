from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional


# Optional heavy dependencies are imported lazily inside functions so that
# tests can run without them being installed. We also expose these as module
# attributes so tests can monkeypatch them.

logger = logging.getLogger(__name__)


try:  # pragma: no cover - optional dependency
    from docx import Document as _DocxDocument  # type: ignore
    Document: Optional[object] = _DocxDocument
except Exception:  # pragma: no cover - missing dependency
    Document = None

try:  # pragma: no cover - optional dependency
    from pdfminer.high_level import extract_text as _extract_text  # type: ignore
    extract_text: Optional[object] = _extract_text
except Exception:  # pragma: no cover - missing dependency
    extract_text = None

class ParseError(Exception):
    pass


def read_file(path: Path) -> str:
    if not path.exists():
        raise ParseError(f"Файл не знайдено: {path}")
    try:
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".docx":
            doc_cls = Document
            if doc_cls is None:
                from docx import Document as _DocxDocument  # type: ignore

                doc_cls = _DocxDocument
            doc = doc_cls(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        if path.suffix.lower() == ".pdf":
            extractor = extract_text
            if extractor is None:
                from pdfminer.high_level import extract_text as _extract_text  # type: ignore

                extractor = _extract_text
            return extractor(str(path))
    except Exception as exc:  # pragma: no cover - logging
        logger.error("Помилка читання %s: %s", path, exc)
        raise ParseError(str(exc))
    raise ParseError(f"Непідтримуваний формат: {path.suffix}")


def find_files(folder: Path, patterns: List[str]) -> List[Path]:
    files: List[Path] = []
    for pattern in patterns:
        files.extend(folder.rglob(pattern))
    return files
