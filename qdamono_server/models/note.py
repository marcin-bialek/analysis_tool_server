from typing import AbstractSet, Any, Mapping, TypedDict
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

    def dict(
        self,
        *args,
        by_alias: bool = True,
        exclude: AbstractSet[int | str] | Mapping[int | str, Any] | None = None,
        **kwargs,
    ) -> NoteDict:
        if exclude is None:
            if isinstance(exclude, set):
                exclude |= {"id"}
            elif isinstance(exclude, dict):
                exclude |= {"id": True}
            else:
                exclude = {"id"}
        self_dict: NoteDict = super().dict(
            *args, exclude=exclude, by_alias=by_alias, **kwargs
        )
        self_dict["_id"] = str(self.id)
        return self_dict

    class Settings:
        name = "notes"
