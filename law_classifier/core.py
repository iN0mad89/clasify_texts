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
        id_документу=path.stem,
        заголовок=None,
        дата=None,
        виявлені_терміни=terms,
        категорія=category,
        додаткові_ознаки=None,
        шлях_файлу=path,
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
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].dict(by_alias=True).keys())
        writer.writeheader()
        for r in results:
            writer.writerow(r.dict(by_alias=True))
