from __future__ import annotations

from typing import AbstractSet, Any, Mapping, TypedDict
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

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> CodingVersionDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True}
            else:
                exclude = {"id"}
        self_dict: CodingVersionDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )
        self_dict["_id"] = str(self.id)
        return self_dict


from qdamono_server.models.coding import Coding, CodingDict

CodingVersion.update_forward_refs()
