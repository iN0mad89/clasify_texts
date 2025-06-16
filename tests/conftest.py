import sys
import types
from pathlib import Path

import pytest


def _simple_yaml_load(text: str):
    data = {}
    current = None
    for line in text.splitlines():
        if line.endswith(":"):
            current = line[:-1]
            data[current] = []
        elif line.strip().startswith("-") and current is not None:
            val = line.split("-", 1)[1].strip().strip('"')
            val = val.replace('\\\\', '\\')
            data[current].append(val)
    return data


@pytest.fixture(autouse=True)
def stub_optional_modules(monkeypatch):
    # stub yaml
    yaml_mod = types.ModuleType("yaml")
    yaml_mod.safe_load = _simple_yaml_load
    sys.modules["yaml"] = yaml_mod

    # stub docx
    docx_mod = types.ModuleType("docx")

    class Document:
        def __init__(self, path):
            text = Path(path).read_text(encoding="utf-8")
            self.paragraphs = [types.SimpleNamespace(text=text)]

    docx_mod.Document = Document
    sys.modules["docx"] = docx_mod

    # stub pdfminer.high_level
    pdfminer_high = types.ModuleType("pdfminer.high_level")

    def extract_text(path: str):
        return Path(path).read_text(encoding="utf-8")

    pdfminer_high.extract_text = extract_text
    sys.modules["pdfminer.high_level"] = pdfminer_high
    pdfminer_mod = types.ModuleType("pdfminer")
    pdfminer_mod.high_level = pdfminer_high
    sys.modules["pdfminer"] = pdfminer_mod

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # stub pydantic BaseModel and Field for schema module
    pydantic_mod = types.ModuleType("pydantic")

    class _Base:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

        def dict(self, *args, **kwargs):
            return self.__dict__

        def json(self, *args, **kwargs):
            import json
            return json.dumps(self.__dict__, ensure_ascii=False, default=str)

    def Field(*args, **kwargs):
        return None

    pydantic_mod.BaseModel = _Base
    pydantic_mod.Field = Field
    sys.modules["pydantic"] = pydantic_mod

    yield

    for name in ["yaml", "docx", "pdfminer", "pdfminer.high_level", "pydantic"]:
        sys.modules.pop(name, None)
