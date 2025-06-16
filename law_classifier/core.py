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
    folder: Path, patterns: Iterable[str], engine: RuleEngine, workers: int = 1
) -> List[DocumentResult]:
    files = find_files(folder, list(patterns))
    results: List[DocumentResult] = []
    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor

        def _worker(path: Path) -> DocumentResult | None:
            try:
                return classify_file(engine, path)
            except Exception as exc:  # pragma: no cover - log and continue
                logger.error("Помилка обробки %s: %s", path, exc)
                return None

        with ThreadPoolExecutor(max_workers=workers) as exc:
            for fut in exc.map(_worker, files):
                if fut is not None:
                    results.append(fut)
    else:
        for file in files:
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
