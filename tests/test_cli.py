from pathlib import Path



from typer.testing import CliRunner

from law_classifier.cli import app



def test_cli_classify(tmp_path):
    from law_classifier.cli import main

    file = tmp_path / "test.txt"
    file.write_text("Постанова про державний бюджет")
    runner = CliRunner()
    result = runner.invoke(app, ["classify", str(file), "--json"])
    assert "BUD" in result.stdout
