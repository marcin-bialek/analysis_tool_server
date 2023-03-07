import inspect
from functools import wraps
from logging import getLogger
from typing import Awaitable, Callable, NewType, TypedDict

import socketio
from beanie import WriteRules
from pydantic.error_wrappers import ValidationError
from pymongo.errors import DuplicateKeyError

from qdamono_server import exceptions, models

logger = getLogger(__name__)

sio = socketio.AsyncServer(async_mode="asgi")


class SessionData(TypedDict):
    client_id: str | None
    username: str | None
    project_id: str | None


SocketIOSession = NewType("SocketIOSession", object)


def project_is_set(
    f: Callable[[SocketIOSession, models.events.BaseEvent], Awaitable[None]]
):
    @wraps(f)
    async def inner(
        self: SocketIOSession, *args, event: models.events.BaseEvent, **kwargs
    ):
        if self.project_id is None:
            raise exceptions.SessionStateError("Project not set.")
        await f(self, *args, event=event, **kwargs)

    return inner


def username_is_set(
    f: Callable[[SocketIOSession, models.events.BaseEvent], Awaitable[None]]
):
    @wraps(f)
    async def inner(
        self: SocketIOSession, *args, event: models.events.BaseEvent, **kwargs
    ):
        if self.username is None:
            raise exceptions.SessionStateError("Username not set.")
        await f(self, *args, event=event, **kwargs)

    return inner


def broadcast_to_project_after(
    f: Callable[[SocketIOSession, models.events.BaseEvent], Awaitable[None]]
):
    @wraps(f)
    async def inner(
        self: SocketIOSession, *args, event: models.events.BaseEvent, **kwargs
    ):
        await f(self, *args, event=event, **kwargs)
        await self.broadcast_to_project(event)

    return inner


class SocketIOSession:
    def __init__(self, session_data: SessionData, sid: str):
        self.data = session_data
        self.sid = sid

    @property
    def client_id(self):
        return self.data.get("client_id")

    @client_id.setter
    def client_id(self, value: str | None):
        logger.debug(f"Changing client_id from {self.client_id} to {value}")
        self.data["client_id"] = value

    @property
    def username(self):
        return self.data.get("username")

    @username.setter
    def username(self, value: str | None):
        logger.debug(f"Changing username from {self.username} to {value}")
        self.data["username"] = value

    @property
    def project_id(self):
        return self.data.get("project_id")

    @project_id.setter
    def project_id(self, value: str | None):
        logger.debug(f"Changing project_id from {self.project_id} to {value}")
        self.data["project_id"] = value

    @classmethod
    async def broadcast_clients_to_project(cls, project_id: str):
        users: dict[str, str] = dict()

        for sid, _ in sio.manager.get_participants(namespace="/", room=project_id):
            session: SessionData = await sio.get_session(sid)
            users[sid] = session.get("username")

        logger.debug(f"Broadcasting participant list of room '{project_id}': {users}")

        event_to_send = models.events.ClientsEvent(clients=users)
        await sio.emit("event", event_to_send.dict(), room=project_id)

    async def send_event(self, event: models.events.BaseEvent):
        await self._send_event_data(event.dict())

    async def _send_event_data(self, data: models.events.BaseEventData):
        await sio.emit("event", data, to=self.sid)

    async def broadcast_to_project(self, event: models.events.BaseEvent):
        await self._broadcast_data_to_project(event.dict())

    async def _broadcast_data_to_project(self, data: models.events.BaseEventData):
        await sio.emit("event", data, room=self.project_id)

    async def enter_project(self, project_id: str):
        if self.project_id is not None:
            await self.leave_project()

        self.project_id = project_id
        sio.enter_room(self.sid, room=project_id)
        await self.broadcast_clients_to_project(project_id)

    async def leave_project(self):
        if self.project_id is None:
            logger.error("Project not set")
            return
        sio.leave_room(self.sid, room=self.project_id)
        await self.broadcast_clients_to_project(self.project_id)
        self.project_id = None

    async def handle_event(self, data: models.events.BaseEventData):
        """Select an event handler from this class based on method name with
        the following format:
            event_<event_name>
        where <event_name> is the 'name' property of the passed data dictionary

        Args:
            data (models.events.BaseEventData): raw event data dictionary
        """
        event_name = data.get("name")
        logger.debug(f"event sid: {self.sid}, name: {event_name}")

        if event_name is None:
            raise exceptions.InvalidEventError("No event name given")

        # Get specific event type
        handler = getattr(self, "event_" + event_name, self.undefined_event)
        parameter_type = inspect.get_annotations(handler).get("event")

        if parameter_type is not None and issubclass(
            parameter_type, models.events.BaseEvent
        ):
            # Validate data by instantiating a pydantic model specific to the event
            try:
                event = parameter_type(**data)
            except ValidationError as e:
                logger.error(f"Passed data might be invalid: {data}")
                raise e

            await handler(event=event)
            return

        # No typing support - pass data as is unchecked
        await handler(data=data)

    # --- Event handlers ---

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_code_add(self, event: models.events.CodeAddEvent):
        project = await models.Project.get(self.project_id)

        if project is None:
            raise exceptions.SessionStateError("Project not found.")

        try:
            await event.code.create()
        except DuplicateKeyError:
            raise Exception(f"Code with id {event.code.id} already exists")

        project.codes.append(event.code)
        await project.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_code_remove(self, event: models.events.CodeRemoveEvent):
        code = await models.Code.get(event.code_id)

        if code is None:
            raise exceptions.DocumentNotFoundError("Code not found.")

        await code.delete()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_code_update(self, event: models.events.CodeUpdateEvent):
        code = await models.Code.get(event.code_id)

        if code is None:
            raise exceptions.DocumentNotFoundError("Code not found.")

        if event.name is not None:
            code.name = event.name

        if event.code_color is not None:
            code.color = event.code_color

        await code.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_coding_add(self, event: models.events.CodingAddEvent):
        coding_version = await models.CodingVersion.get(event.coding_version_id)

        if coding_version is None:
            raise exceptions.DocumentNotFoundError("Coding version not found.")

        coding_version.codings.append(event.coding)
        await coding_version.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_coding_remove(self, event: models.events.CodingRemoveEvent):
        coding_version = await models.CodingVersion.get(event.coding_version_id)

        if coding_version is None:
            raise exceptions.DocumentNotFoundError("Coding version not found.")

        coding_version.codings.remove(event.coding)
        await coding_version.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_coding_version_add(
        self, event: models.events.CodingVersionAddEvent
    ):
        text_file = await models.TextFile.get(event.text_file_id)

        if text_file is None:
            raise exceptions.DocumentNotFoundError("Text file not found.")

        await event.coding_version.create()

        text_file.coding_versions.append(event.coding_version)
        await text_file.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_coding_version_remove(
        self, event: models.events.CodingVersionRemoveEvent
    ):
        coding_version = await models.CodingVersion.get(event.coding_version_id)

        if coding_version is None:
            raise Exception("Coding version not found")

        text_file = await models.TextFile.get(event.text_file_id)

        if text_file is None:
            raise exceptions.DocumentNotFoundError("Text file not found")

        await coding_version.delete()

        for i, coding_version_link in enumerate(text_file.coding_versions):
            if coding_version_link.ref.id == coding_version.id:
                text_file.coding_versions.pop(i)
        await text_file.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_coding_version_update(
        self, event: models.events.CodingVersionUpdateEvent
    ):
        coding_version = await models.CodingVersion.get(event.coding_version_id)

        if coding_version is None:
            raise exceptions.DocumentNotFoundError("Coding version not found")

        coding_version.name = event.coding_version_name
        await coding_version.save()

    async def event_hello(self, event: models.events.HelloEvent):
        self.client_id = event.client_id
        self.username = event.username

    @username_is_set
    async def event_logout(self, event: models.events.LogoutEvent):
        logger.info(f"{self.username} is logging out")

        if self.project_id is not None:
            await self.leave_project()

        self.client_id = None
        self.username = None

    @username_is_set
    async def event_get_project(self, event: models.events.GetProjectEvent):
        logger.debug(f"passcode {event.passcode}")
        project = await models.Project.get(event.passcode)

        if project is not None:
            await self.enter_project(event.passcode)
            await project.fetch_all_links()

        event_to_send = models.events.ProjectEvent(project=project)
        await self.send_event(event_to_send)

    async def event_get_project_data(self, event: models.events.GetProjectEvent):
        logger.debug(f"passcode {event.passcode}")
        project = await models.Project.get(event.passcode)

        if project is not None:
            await self.enter_project(event.passcode)
            await project.fetch_all_links()

        event_to_send = models.events.ProjectEvent(project=project)
        await self.send_event(event_to_send)

    @username_is_set
    @project_is_set
    async def event_leave_project(self, event: models.events.LeaveProjectEvent):
        await self.leave_project()

    @username_is_set
    async def event_publish_project(self, event: models.events.PublishProjectEvent):
        if event.project is None:
            raise exceptions.InvalidEventError("project is None.")

        try:
            await event.project.insert(link_rule=WriteRules.WRITE)
        except DuplicateKeyError:
            raise exceptions.DocumentAlreadyExistsError(
                f"Project with id {event.project.id} already exists"
            )

        self.project_id = event.project.id

        published_event = models.events.PublishedEvent(
            name="published", passcode=str(event.project.id)
        )
        await self.send_event(published_event)

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_note_add_to_line(self, event: models.events.NoteAddToLineEvent):
        note = await models.Note.get(event.note_id)

        if note is None:
            raise exceptions.DocumentNotFoundError("Note not found.")

        if event.coding_version_id not in note.text_lines:
            note.text_lines[event.coding_version_id] = [event.line_index]
        else:
            note.text_lines[event.coding_version_id].append(event.line_index)

        await note.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_note_add(
        self, event: models.events.NoteAddEvent, project: models.Project
    ):
        try:
            await event.note.create()
        except DuplicateKeyError:
            raise exceptions.DocumentAlreadyExistsError(
                f"Note with id {event.note.id} already exists"
            )

        project.notes.append(event.note)
        await project.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_note_remove_from_line(
        self, event: models.events.NoteRemoveFromLineEvent
    ):
        note = await models.Note.get(event.note_id)

        if note is None:
            raise exceptions.DocumentNotFoundError("Note not found.")

        if event.coding_version_id not in note.text_lines:
            raise exceptions.DocumentError("No line entries for this coding version.")
        else:
            note.text_lines[event.coding_version_id].remove(event.line_index)

        await note.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_note_remove(self, event: models.events.NoteRemoveEvent):
        note = await models.Note.get(event.note_id)

        if note is None:
            raise exceptions.DocumentNotFoundError("Note not found.")

        await note.delete()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_note_update(self, event: models.events.NoteUpdateEvent):
        note = await models.Note.get(event.note_id)

        if note is None:
            raise exceptions.DocumentNotFoundError("Note not found.")

        if event.title is not None:
            note.title = event.title

        if event.text is not None:
            note.text = event.text

        await note.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_text_file_add(self, event: models.events.TextFileAddEvent):
        project = await models.Project.get(self.project_id)

        if project is None:
            raise exceptions.SessionStateError("Project not found.")

        try:
            await event.text_file.create()
        except DuplicateKeyError:
            raise exceptions.DocumentAlreadyExistsError(
                f"Text file with id {event.text_file.id} already exists."
            )

        project.text_files.append(event.text_file)
        await project.save()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_text_file_remove(self, event: models.events.TextFileRemoveEvent):
        text_file = await models.TextFile.get(event.text_file_id)

        if text_file is None:
            raise exceptions.DocumentNotFoundError("Text file not found")

        await text_file.delete()

    @username_is_set
    @project_is_set
    @broadcast_to_project_after
    async def event_text_file_update(self, event: models.events.TextFileUpdateEvent):
        text_file = await models.TextFile.get(event.text_file_id)

        if text_file is None:
            raise exceptions.DocumentNotFoundError("Text file not found.")

        if event.text_file_name is not None:
            text_file.name = event.text_file_name

        if event.text is not None:
            text_file.text = event.text

        await text_file.save()

    async def undefined_event(self, data: models.events.BaseEvent):
        raise exceptions.InvalidEventError(f"Unknown event: {data.name}")
