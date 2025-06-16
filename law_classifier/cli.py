from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from .core import classify_file
from .io_utils import find_files
from .rules import RuleEngine


def get_engine() -> RuleEngine:
    return RuleEngine(Path(__file__).resolve().parent.parent / "data" / "terms.yaml")


def cmd_classify(args: argparse.Namespace) -> None:
    engine = get_engine()
    result = classify_file(engine, Path(args.path))
    if args.json:
        print(result.json(by_alias=True, ensure_ascii=False))
    else:
        print(result)


def cmd_batch(args: argparse.Namespace) -> None:
    engine = get_engine()
    files = find_files(Path(args.folder), ["*.txt", "*.docx", "*.pdf"])
    results = []

    def _worker(path: Path):
        try:
            return classify_file(engine, path)
        except Exception as exc:  # pragma: no cover - logging
            logging.error("Помилка обробки %s: %s", path, exc)
            return None

    with ThreadPoolExecutor(max_workers=args.workers) as exc:
        futs = [exc.submit(_worker, f) for f in files]
        for fut in as_completed(futs):
            res = fut.result()
            if res is not None:
                results.append(res)

    rows = [r.dict(by_alias=True) for r in results]
    if args.out:
        import csv

        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    if args.html:
        html_path = (
            Path(args.out).with_suffix(".html") if args.out else Path("results.html")
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(
                "<table><tr>"
                + "".join(f"<th>{k}</th>" for k in rows[0].keys())
                + "</tr>"
            )
            for row in rows:
                f.write(
                    "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
                )
            f.write("</table>")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="law_classifier")
    subparsers = parser.add_subparsers(dest="command")

    p_classify = subparsers.add_parser("classify")
    p_classify.add_argument("path")
    p_classify.add_argument("--json", action="store_true")
    p_classify.set_defaults(func=cmd_classify)

    p_batch = subparsers.add_parser("batch")
    p_batch.add_argument("folder")
    p_batch.add_argument("--out")
    p_batch.add_argument("--html", action="store_true")
    p_batch.add_argument("--workers", type=int, default=1)
    p_batch.set_defaults(func=cmd_batch)
    return parser


def main(args: Optional[List[str]] = None) -> None:
    parser = build_parser()
    ns = parser.parse_args(args)
    if hasattr(ns, "func"):
        ns.func(ns)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
