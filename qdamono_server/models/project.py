from __future__ import annotations

from typing import AbstractSet, Any, Mapping, TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field


class ProjectDict(TypedDict):
    _id: str
    name: str
    codes: list[CodeDict]
    notes: list[NoteDict]
    text_files: list[TextFileDict]


class Project(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    codes: list[Link[Code]]
    notes: list[Link[Note]]
    text_files: list[Link[TextFile]]

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> ProjectDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True}
            else:
                exclude = {"id"}
        self_dict: ProjectDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )
        self_dict["_id"] = str(self.id)
        return self_dict

    class Settings:
        name = "projects"


from qdamono_server.models.code import Code, CodeDict
from qdamono_server.models.note import Note, NoteDict
from qdamono_server.models.text_file import TextFile, TextFileDict

Project.update_forward_refs()
