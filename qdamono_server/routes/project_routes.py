from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from qdamono_server.auth.models.user import User
from qdamono_server.auth.users import current_active_user
from qdamono_server.exceptions import DocumentNotFoundError, AuthorizationError
from qdamono_server.repos import project_repo
from qdamono_server.settings import settings

router = APIRouter()
logger = settings.logging.get_logger(__name__)


@router.get("/{id}")
async def get_project(id: str, user: User = Depends(current_active_user)):
    try:
        uuid_id = UUID(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID"
        )

    try:
        project = await project_repo.get(uuid_id, user)
    except (DocumentNotFoundError, AuthorizationError) as e:
        logger.error(str(e))
        # Do not leak project IDs by returning an 'unauthorized' message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return project


@router.get("/")
async def get_project_list(user: User = Depends(current_active_user)):
    return await project_repo.get_project_list(user=user)
