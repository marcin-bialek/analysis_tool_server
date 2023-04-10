from fastapi import Depends
from fastapi.routing import APIRouter

from qdamono_server.auth.models.user import User
from qdamono_server.auth.users import current_active_user
from qdamono_server.models.project_privilege import ProjectPrivilege

router = APIRouter()


@router.get("/")
async def get_project_privilege_list(user: User = Depends(current_active_user)):
    project_privilege_list = await ProjectPrivilege.find_many(
        ProjectPrivilege.user.id == user.id
    ).to_list()

    return [p.dict() for p in project_privilege_list]
