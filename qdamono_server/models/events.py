from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field


class BaseEventData(TypedDict):
    name: str


class BaseEvent(BaseModel):
    name: str


class GetClientIdEvent(BaseEvent):
    name: str = Field("get_client_id", const=True)


class ClientIdEvent(BaseEvent):
    name: str = Field("client_id", const=True)
    client_id: str


class ClientsEvent(BaseEvent):
    name: str = Field("clients", const=True)
    clients: dict[str, str]


class BaseCodeEvent(BaseEvent):
    pass


class CodeAddEvent(BaseCodeEvent):
    name: str = Field("code_add", const=True)
    code: Code


class CodeRemoveEvent(BaseEvent):
    name: str = Field("code_remove", const=True)
    code_id: str


class CodeUpdateEvent(BaseCodeEvent):
    name: str = Field("code_update", const=True)
    code_id: str | None
    code_name: str | None
    code_color: str | None


class BaseCodingEvent(BaseEvent):
    pass


class CodingAddEvent(BaseCodingEvent):
    name: str = Field("coding_add", const=True)
    text_file_id: str
    coding_version_id: str
    coding_line_index: int
    coding: Coding


class CodingRemoveEvent(BaseCodingEvent):
    name: str = Field("coding_remove", const=True)
    text_file_id: str
    coding_version_id: str
    coding: Coding


class BaseCodingVersionEvent(BaseEvent):
    pass


class CodingVersionAddEvent(BaseCodingVersionEvent):
    name: str = Field("coding_version_add", const=True)
    text_file_id: str
    coding_version: CodingVersion


class CodingVersionRemoveEvent(BaseCodingVersionEvent):
    name: str = Field("coding_version_remove", const=True)
    text_file_id: str
    coding_version_id: str


class CodingVersionUpdateEvent(BaseCodingVersionEvent):
    name: str = Field("coding_version_update", const=True)
    text_file_id: str
    coding_version_id: str
    coding_version_name: str | None


class LogoutEvent(BaseEvent):
    name: str = Field("logout", const=True)


class BaseProjectEvent(BaseEvent):
    pass


class GetProjectEvent(BaseProjectEvent):
    name: str = Field("get_project", const=True)
    passcode: str


class LeaveProjectEvent(BaseProjectEvent):
    pass


class ProjectEvent(BaseProjectEvent):
    name: str = Field("project", const=True)
    project: Project | None


class PublishProjectEvent(BaseProjectEvent):
    name: str = Field("publish_project", const=True)
    project: Project


class PublishedEvent(BaseProjectEvent):
    name: str = Field("published", const=True)
    passcode: str


class BaseNoteEvent(BaseEvent):
    pass


class NoteAddToLineEvent(BaseNoteEvent):
    name: str = Field("note_add_to_line", const=True)
    coding_version_id: str
    line_index: int
    note_id: str


class NoteAddEvent(BaseNoteEvent):
    name: str = Field("note_add", const=True)
    note: Note


class NoteRemoveFromLineEvent(BaseNoteEvent):
    name: str = Field("note_remove_from_line", const=True)
    coding_version_id: str
    line_index: int
    note_id: str


class NoteRemoveEvent(BaseNoteEvent):
    name: str = Field("note_remove", const=True)
    note_id: str


class NoteUpdateEvent(BaseNoteEvent):
    name: str = Field("note_update", const=True)
    note_id: str
    title: str | None
    text: str | None


class TextFileEvent(BaseEvent):
    pass


class TextFileAddEvent(TextFileEvent):
    name: str = Field("text_file_add", const=True)
    text_file: TextFile


class TextFileRemoveEvent(TextFileEvent):
    name: str = Field("text_file_remove", const=True)
    text_file_id: str


class TextFileUpdateEvent(TextFileEvent):
    name: str = Field("text_file_update", const=True)
    text_file_id: str
    text_file_name: str | None
    text: str | None


from qdamono_server.models.code import Code
from qdamono_server.models.coding import Coding
from qdamono_server.models.coding_version import CodingVersion
from qdamono_server.models.note import Note
from qdamono_server.models.project import Project
from qdamono_server.models.text_file import TextFile

CodeAddEvent.update_forward_refs()
CodingAddEvent.update_forward_refs()
CodingRemoveEvent.update_forward_refs()
CodingVersionAddEvent.update_forward_refs()
NoteAddEvent.update_forward_refs()
ProjectEvent.update_forward_refs()
PublishProjectEvent.update_forward_refs()
TextFileAddEvent.update_forward_refs()
