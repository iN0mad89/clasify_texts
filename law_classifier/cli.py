from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from .core import batch as batch_core, classify_file
from .rules import RuleEngine

app = typer.Typer(help="Utilities for classifying Ukrainian legal texts")


def get_engine() -> RuleEngine:
    """Return a rule engine initialised with packaged terms."""
    from importlib import resources

    try:
        pkg = "law_classifier.data"
        data_path = resources.files(pkg) / "terms.yaml"
    except ModuleNotFoundError:  # pragma: no cover - local source layout
        pkg = "data"
        data_path = resources.files(pkg) / "terms.yaml"

    with resources.as_file(data_path) as path:
        return RuleEngine(Path(path))


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
