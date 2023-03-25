from enum import IntEnum
from typing import AbstractSet, Any, Mapping, TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field

from qdamono_server.models.project import Project
from qdamono_server.auth.models.user import User


class ProjectPrivilegeLevel(IntEnum):
    OWNER = 0
    MAINTAINER = 10
    CONTRIBUTOR = 20
    GUEST = 30


class ProjectPrivilegeDict(TypedDict):
    _id: str
    level: int
    user_id: str
    project_id: str


class ProjectPrivilege(Document):
    id: UUID = Field(default_factory=uuid4)
    level: ProjectPrivilegeLevel
    user: Link[User] = Field(..., alias="user_id")
    project: Link[Project] = Field(..., alias="project_id")

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> ProjectPrivilegeDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id", "project", "user"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True, "project": True, "user": True}
            else:
                exclude = {"id", "project", "user"}

        self_dict: ProjectPrivilegeDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )

        self_dict["_id"] = str(self.id)

        if self.project is not None:
            if isinstance(self.project, Link):
                self.project: Link
                self_dict["project_id"] = str(self.project.ref.id)
            elif isinstance(self.project, Project):
                self.project: Project
                self_dict["project_id"] = str(self.project.id)

        if self.user is not None:
            if isinstance(self.user, Link):
                self.user: Link
                self_dict["user_id"] = str(self.user.ref.id)
            elif isinstance(self.user, User):
                self.user: User
                self_dict["user_id"] = str(self.user.id)

        return self_dict

    class Settings:
        name = "project_privileges"
