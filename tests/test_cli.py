from pathlib import Path



from typer.testing import CliRunner

from law_classifier.cli import app



def test_cli_classify(tmp_path):
    from law_classifier.cli import main

    file = tmp_path / "test.txt"
    file.write_text("Постанова про державний бюджет")

    # capture output
    import sys
    from io import StringIO

    buf = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buf
    try:
        main(["classify", str(file), "--json"])
    finally:
        sys.stdout = sys_stdout
    out = buf.getvalue()
    assert "BUD" in out


def test_cli_batch_multiworker(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("Постанова про державний бюджет")
    f2 = tmp_path / "b.txt"
    f2.write_text("Науковець отримав грант")

    import json
    import sys
    from io import StringIO

    buf = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buf
    try:
        main(["batch", str(tmp_path), "--workers", "2"])
    finally:
        sys.stdout = sys_stdout
    data = json.loads(buf.getvalue())
    categories = {d["категорія"] for d in data}
    assert {"BUD", "SCI"} <= categories

    runner = CliRunner()
    result = runner.invoke(app, ["classify", str(file), "--json"])
    assert "BUD" in result.stdout

