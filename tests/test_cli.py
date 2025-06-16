from pathlib import Path

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
