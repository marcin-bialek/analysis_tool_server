from fastapi import Depends
from fastapi.routing import APIRouter

from qdamono_server.auth.models.user import User
from qdamono_server.auth.users import current_active_user
from qdamono_server.models import Project
from qdamono_server.models.events import ProjectInfo

router = APIRouter()


@router.get("/")
async def get_project_list(user: User = Depends(current_active_user)):
    project_list = await Project.find_all().to_list()

    project_info_list = [
        ProjectInfo(id=str(project.id), name=project.name) for project in project_list
    ]

    return project_info_list
