from enum import IntEnum
from typing import TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field
import pymongo

from qdamono_server.models.project import Project
from qdamono_server.auth.models.user import User


class ProjectPrivilegeLevel(IntEnum):
    UNAUTHORIZED = 0
    GUEST = 10
    CONTRIBUTOR = 20
    MAINTAINER = 30
    OWNER = 40


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

    def dict(self, by_alias: bool = True) -> ProjectPrivilegeDict:
        self_dict: ProjectPrivilegeDict = super().dict(
            exclude={"id", "project", "user"}, by_alias=by_alias
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
        indexes = [
            pymongo.IndexModel(
                [("user_id", pymongo.TEXT), ("project_id", pymongo.TEXT)],
                unique=True,
            )
        ]
