from __future__ import annotations

from typing import TypedDict
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field


class ProjectDict(TypedDict):
    _id: str
    name: str
    is_public: bool
    codes: list[CodeDict]
    notes: list[NoteDict]
    text_files: list[TextFileDict]


class Project(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    is_public: bool = Field(False)
    codes: list[Link[Code]]
    notes: list[Link[Note]]
    text_files: list[Link[TextFile]]

    def dict(self, by_alias: bool = True) -> ProjectDict:
        self_dict: ProjectDict = super().dict(exclude={"id"}, by_alias=by_alias)
        self_dict["_id"] = str(self.id)
        return self_dict


from qdamono_server.models.code import Code, CodeDict
from qdamono_server.models.note import Note, NoteDict
from qdamono_server.models.text_file import TextFile, TextFileDict

Project.update_forward_refs()
