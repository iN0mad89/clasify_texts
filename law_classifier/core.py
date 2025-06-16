from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Iterable, List

from .io_utils import find_files, read_file
from .rules import RuleEngine
from .schema import DocumentResult

logger = logging.getLogger(__name__)


def classify_file(engine: RuleEngine, path: Path) -> DocumentResult:
    text = read_file(path)
    category, terms = engine.match(text)
    return DocumentResult(
        id_document=path.stem,
        category=category,
        title=None,
        date=None,
        terms=terms,
        extra=None,
        path=path,
    )


def batch(
    folder: Path, patterns: Iterable[str], engine: RuleEngine
) -> List[DocumentResult]:
    results: List[DocumentResult] = []
    for file in find_files(folder, list(patterns)):
        try:
            results.append(classify_file(engine, file))
        except Exception as exc:  # pragma: no cover - log and continue
            logger.error("Помилка обробки %s: %s", file, exc)
    return results


def save_csv(results: List[DocumentResult], path: Path) -> None:
    """Save classification results to CSV.

    If *results* is empty, an empty file with only the header will be created
    and a warning logged.
    """

    fieldnames = [
        f.metadata.get("alias", name)
        for name, f in DocumentResult.__dataclass_fields__.items()
    ]

    if not results:
        logger.warning("No results provided to save_csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.dict(by_alias=True))
