from typing import TypedDict
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class NoteDict(TypedDict):
    _id: str
    title: str
    text: str
    textLines: str


class Note(Document):
    id: UUID = Field(default_factory=uuid4)
    title: str
    text: str
    text_lines: dict[str, list[int]] = dict()

    def dict(self, by_alias: bool = True) -> NoteDict:
        self_dict: NoteDict = super().dict(exclude={"id"}, by_alias=by_alias)
        self_dict["_id"] = str(self.id)
        return self_dict
