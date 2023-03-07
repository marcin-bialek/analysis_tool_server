from __future__ import annotations

from typing import AbstractSet, Any, Mapping, TypedDict
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

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> TextFileDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True}
            else:
                exclude = {"id"}
        self_dict: TextFileDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )
        self_dict["_id"] = str(self.id)
        return self_dict

    class Settings:
        name = "text_files"