from __future__ import annotations

from typing import TypedDict

from beanie import Link
from pydantic import BaseModel, Field


class CodingDict(TypedDict):
    code_id: str
    start: int
    length: int


class Coding(BaseModel):
    code: Link[Code] = Field(alias="code_id")
    start: int
    length: int

    def dict(
        self,
        by_alias: bool = True,
    ) -> CodingDict:
        self_dict: CodingDict = super().dict(exclude={"code"}, by_alias=by_alias)

        if isinstance(self.code, Link):
            self.code: Link
            self_dict["code_id"] = str(self.code.ref.id)
        elif isinstance(self.code, Code):
            self.code: Code
            self_dict["code_id"] = str(self.code.id)

        return self_dict


from qdamono_server.models.code import Code

Coding.update_forward_refs()
