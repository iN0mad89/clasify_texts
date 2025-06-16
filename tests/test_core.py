from pathlib import Path
import csv


def test_batch_and_save_csv(tmp_path):
    from law_classifier.core import batch, save_csv
    from law_classifier.rules import RuleEngine

    engine = RuleEngine(Path("data/terms.yaml"))
    f1 = tmp_path / "a.txt"
    f1.write_text("Постанова про державний бюджет")
    f2 = tmp_path / "b.txt"
    f2.write_text("Простий текст")

    results = batch(tmp_path, ["*.txt"], engine)
    assert len(results) == 2
    cats = {getattr(r, "категорія", None) for r in results}
    assert {"BUD", "UNLABELLED"} <= cats

    csv_path = tmp_path / "res.csv"
    save_csv(results, csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert {row["категорія"] for row in rows} == cats
