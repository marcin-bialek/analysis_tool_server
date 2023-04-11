from __future__ import annotations

from typing import TypedDict
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class CodingVersionDict(TypedDict):
    _id: str
    name: str
    codings: list[CodingDict]


class CodingVersion(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    codings: list[Coding]

    def dict(self, by_alias: bool = True, **kwargs) -> CodingVersionDict:
        self_dict: CodingVersionDict = super().dict(exclude={"id"}, by_alias=by_alias)
        self_dict["_id"] = str(self.id)
        return self_dict


from qdamono_server.models.coding import Coding, CodingDict

CodingVersion.update_forward_refs()
