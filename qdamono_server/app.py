from logging import getLogger

import socketio
from fastapi import FastAPI

import qdamono_server.db as db
from qdamono_server.event_handling import sio, SessionData, SocketIOSession

logger = getLogger(__name__)

app = FastAPI(debug=True, root_path="/")
sio_app = socketio.ASGIApp(sio, socketio_path="/")

app.mount("/socket.io/", sio_app)


@app.get("/")
async def root():
    return "This is QDAmono v2.0.0!"


@app.on_event("startup")
async def start_db():
    await db.init_db()


@sio.on("connect")
async def on_connect(sid: str, env: dict, auth: str | None = None):
    logger.debug(f"connect {sid}")
    # logger.debug(", ".join([f"{k}: {v}" for k, v in env.items()]))
    # TODO: authenticate user
    await sio.save_session(sid, SessionData())


@sio.on("event")
async def on_event(sid: str, data: dict):
    async with sio.session(sid) as session_data:
        logger.debug(f"session_data: {session_data}")
        session = SocketIOSession(session_data, sid)
        await session.handle_event(data)


@sio.on("disconnect")
async def on_disconnect(sid: str):
    logger.debug(f"disconnect {sid}")
    async with sio.session(sid) as session_data:
        session = SocketIOSession(session_data, sid)
        if session.project_id is not None:
            await session.leave_project()
