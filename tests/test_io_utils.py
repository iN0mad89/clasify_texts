from pathlib import Path
import pytest


def test_read_file_missing_docx(monkeypatch, tmp_path):
    from law_classifier import io_utils

    doc = tmp_path / "file.docx"
    doc.write_text("text")
    monkeypatch.setattr(io_utils, "Document", lambda path: (_ for _ in ()).throw(ImportError("no docx")))
    with pytest.raises(io_utils.ParseError):
        io_utils.read_file(doc)


def test_read_file_missing_pdf(monkeypatch, tmp_path):
    from law_classifier import io_utils

    pdf = tmp_path / "file.pdf"
    pdf.write_text("text")
    monkeypatch.setattr(io_utils, "extract_text", lambda path: (_ for _ in ()).throw(ImportError("no pdf")))
    with pytest.raises(io_utils.ParseError):
        io_utils.read_file(pdf)
