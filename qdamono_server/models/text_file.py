from __future__ import annotations

from typing import TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field

from qdamono_server.models.coding_version import CodingVersion, CodingVersionDict


class TextFileDict(TypedDict):
    _id: str
    name: str
    text: str
    coding_versions: list[CodingVersionDict]


class TextFile(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    text: str
    coding_versions: list[Link[CodingVersion]]

    def dict(self, by_alias: bool = True, **kwargs) -> TextFileDict:
        self_dict: TextFileDict = super().dict(exclude={"id"}, by_alias=by_alias)
        self_dict["_id"] = str(self.id)
        return self_dict
