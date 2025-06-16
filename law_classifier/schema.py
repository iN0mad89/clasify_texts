from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class DocumentResult:
    id_document: str = field(metadata={"alias": "id_документу"})
    category: str = field(metadata={"alias": "категорія"})
    title: Optional[str] = field(default=None, metadata={"alias": "заголовок"})
    date: Optional[str] = field(default=None, metadata={"alias": "дата"})
    terms: List[str] = field(default_factory=list, metadata={"alias": "виявлені_терміни"})
    extra: Optional[str] = field(default=None, metadata={"alias": "додаткові_ознаки"})
    path: Path = field(default_factory=Path, metadata={"alias": "шлях_файлу"})

    def __getattr__(self, item: str):  # pragma: no cover - simple alias access
        for name, f in self.__dataclass_fields__.items():
            if f.metadata.get("alias") == item:
                return getattr(self, name)
        raise AttributeError(item)

    def dict(self, *, by_alias: bool = False) -> dict:
        data = asdict(self)
        if isinstance(data.get("path"), Path):
            data["path"] = str(data["path"])
        if by_alias:
            return {
                f.metadata.get("alias", name): data[name]
                for name, f in self.__dataclass_fields__.items()
            }
        return data

    def json(self, *, by_alias: bool = False, ensure_ascii: bool = False) -> str:
        return json.dumps(self.dict(by_alias=by_alias), ensure_ascii=ensure_ascii)
