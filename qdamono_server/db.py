import beanie as odm
from motor.motor_asyncio import AsyncIOMotorClient

from qdamono_server import models
from qdamono_server.auth import models as auth_models
from qdamono_server.settings import settings

logger = settings.logging.get_logger(__name__)


async def init_db():
    logger.debug("Establishing database connection...")

    await odm.init_beanie(
        database=AsyncIOMotorClient(
            settings.db_url, uuidRepresentation="standard"
        ).qdamono,
        document_models=[
            models.Project,
            models.Code,
            models.Note,
            models.TextFile,
            models.CodingVersion,
            auth_models.User,
            auth_models.AccessToken,
            models.ProjectPrivilege,
        ],
    )
