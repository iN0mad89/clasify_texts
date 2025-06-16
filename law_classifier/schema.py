from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentResult(BaseModel):
    id_document: str = Field(alias="id_документу")
    title: Optional[str] = Field(default=None, alias="заголовок")
    date: Optional[str] = Field(default=None, alias="дата")
    terms: List[str] = Field(default_factory=list, alias="виявлені_терміни")
    category: str = Field(alias="категорія")
    extra: Optional[str] = Field(default=None, alias="додаткові_ознаки")
    path: Path = Field(alias="шлях_файлу")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
