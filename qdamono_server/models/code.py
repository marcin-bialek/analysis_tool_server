from __future__ import annotations

from typing import AbstractSet, Any, Mapping, NotRequired, TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field


class CodeDict(TypedDict):
    _id: str
    name: str
    color: int
    parent_id: NotRequired[str]


class Code(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    color: int
    parent: Link[Code] | None = Field(alias="parent_id")

    def dict(self, by_alias: bool = True, **kwargs) -> CodeDict:
        self_dict: CodeDict = super().dict(exclude={"id", "parent"}, by_alias=by_alias)

        self_dict["_id"] = str(self.id)

        if self.parent is not None:
            if isinstance(self.parent, Link):
                self.parent: Link
                self_dict["parent_id"] = str(self.parent.ref.id)
            elif isinstance(self.parent, Code):
                self.parent: Code
                self_dict["parent_id"] = str(self.parent.id)

        return self_dict


Code.update_forward_refs()
