from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Any
import json


@dataclass
class DocumentResult:
    id_документу: str
    заголовок: Optional[str] = None
    дата: Optional[str] = None
    виявлені_терміни: List[str] = field(default_factory=list)
    категорія: str = ""
    додаткові_ознаки: Optional[str] = None
    шлях_файлу: Path = Path()

    def dict(self, *, by_alias: bool = True) -> dict[str, Any]:
        data = asdict(self)
        data["шлях_файлу"] = str(data["шлях_файлу"])
        return data

    def json(self, **kwargs: Any) -> str:
        kwargs.pop("by_alias", None)
        return json.dumps(self.dict(), **kwargs)
