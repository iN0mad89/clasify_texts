from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional


from .core import classify_file
from .io_utils import find_files

import typer

from .core import batch as batch_core, classify_file

from .rules import RuleEngine

app = typer.Typer(help="Utilities for classifying Ukrainian legal texts")


def get_engine() -> RuleEngine:
    """Return a rule engine initialised with packaged terms."""
    return RuleEngine(Path(__file__).resolve().parent.parent / "data" / "terms.yaml")


@app.command()
def classify(path: Path, json_: bool = typer.Option(False, "--json", help="Output JSON")) -> None:
    """Classify a single file."""
    engine = get_engine()
    result = classify_file(engine, path)
    if json_:
        typer.echo(result.json(by_alias=True, ensure_ascii=False))
    else:
        typer.echo(str(result))


@app.command()
def batch(
    folder: Path,
    out: Optional[Path] = typer.Option(None, help="Save results to CSV"),
    html: bool = typer.Option(False, help="Also save HTML table"),
    workers: int = typer.Option(1, help="Number of workers"),
) -> None:
    """Classify all supported files in a folder."""
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


    results = batch_core(folder, ["*.txt", "*.docx", "*.pdf"], engine)

    rows = [r.dict(by_alias=True) for r in results]
    if out:
        import csv

        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    if html:
        html_path = out.with_suffix(".html") if out else Path("results.html")
        with html_path.open("w", encoding="utf-8") as f:
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
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


def main(args: Optional[List[str]] = None) -> None:
    """Entry point for setuptools."""
    app(args=args)


if __name__ == "__main__":  # pragma: no cover
    main()
