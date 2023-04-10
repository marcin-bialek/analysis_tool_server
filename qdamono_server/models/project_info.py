from __future__ import annotations

from typing import AbstractSet, Any, Mapping, TypedDict
from uuid import UUID

from pydantic import BaseModel

from qdamono_server.models.project_privilege import ProjectPrivilegeLevel


class ProjectInfoDict(TypedDict):
    _id: str
    name: str
    privilege: int


class ProjectInfo(BaseModel):
    id: UUID
    name: str
    privilege: ProjectPrivilegeLevel

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> ProjectInfoDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True}
            else:
                exclude = {"id"}
        self_dict: ProjectInfoDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )
        self_dict["_id"] = str(self.id)
        return self_dict
