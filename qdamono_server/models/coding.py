from __future__ import annotations

from typing import AbstractSet, Any, Mapping, TypedDict

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
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> CodingDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"code"}
            elif isinstance(exclude, dict):
                exclude |= {"code": True}
            else:
                exclude = {"code"}

        self_dict: CodingDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )

        if isinstance(self.code, Link):
            self.code: Link
            self_dict["code_id"] = str(self.code.ref.id)
        elif isinstance(self.code, Code):
            self.code: Code
            self_dict["code_id"] = str(self.code.id)

        return self_dict


from qdamono_server.models.code import Code

Coding.update_forward_refs()
