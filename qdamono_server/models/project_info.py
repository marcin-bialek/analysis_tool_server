from __future__ import annotations

from typing import TypedDict
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

    def dict(self, by_alias: bool = True, **kwargs) -> ProjectInfoDict:
        self_dict: ProjectInfoDict = super().dict(exclude={"id"}, by_alias=by_alias)
        self_dict["_id"] = str(self.id)
        return self_dict
