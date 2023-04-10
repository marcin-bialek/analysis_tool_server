from uuid import UUID

from beanie import WriteRules
from pymongo.errors import DuplicateKeyError

from qdamono_server.auth.models import User
from qdamono_server.exceptions import (
    AuthorizationError,
    DocumentNotFoundError,
    DuplicateDocumentError,
)
from qdamono_server.models import (
    Project,
    ProjectInfo,
    ProjectPrivilege,
    ProjectPrivilegeLevel,
)
from qdamono_server.settings import settings

logger = settings.logging.get_logger(__name__)


class ProjectRepository:
    @classmethod
    async def get(cls, id: UUID, user: User, fetch_links: bool = True):
        project = await Project.get(id)

        if project is None:
            raise DocumentNotFoundError(f"Project {str(id)} not found")

        privilege = await ProjectPrivilege.find_one(
            ProjectPrivilege.user.id == user.id
            and ProjectPrivilege.project.id == project.id
        )

        privilege_level = (
            privilege.level
            if privilege is not None
            else ProjectPrivilegeLevel.GUEST
            if project.is_public
            else ProjectPrivilegeLevel.UNAUTHORIZED
        )

        if privilege_level < ProjectPrivilegeLevel.GUEST:
            raise AuthorizationError(
                f"User {user.email} is unauthorized to access project {str(project.id)}"
            )

        if fetch_links:
            await project.fetch_all_links()

        return project

    @classmethod
    async def create(cls, project: Project, user: User):
        privilege = ProjectPrivilege(
            project_id=project.id, user_id=user.id, level=ProjectPrivilegeLevel.OWNER
        )

        try:
            await project.insert(link_rule=WriteRules.WRITE)
            await privilege.insert(link_rule=WriteRules.DO_NOTHING)
        except DuplicateKeyError:
            raise DuplicateDocumentError(
                f"Project with id {str(project.id)} already exists"
            )

    @classmethod
    async def get_project_list(cls, user: User):
        project_info_list: list[ProjectInfo] = []
        # Querrying link IDs that are of UUID type is currently broken in beanie
        privilege_list = await ProjectPrivilege.find_all().to_list()

        async for project in Project.find_all():
            # This does not work in current version of beanie:
            # privilege = await ProjectPrivilege.find_one(
            #     ProjectPrivilege.user.id == user.id
            #     ProjectPrivilege.project.id == project.id,
            # )

            privilege_level = await cls.get_privilege_level(
                project=project, user=user, privilege_list=privilege_list
            )

            if privilege_level >= ProjectPrivilegeLevel.GUEST:
                project_info_list.append(
                    ProjectInfo(
                        id=str(project.id), name=project.name, privilege=privilege_level
                    )
                )

        return project_info_list

    @classmethod
    async def get_privilege_level(
        cls,
        project: Project,
        user: User,
        privilege_list: list[ProjectPrivilege] | None = None,
    ):
        if privilege_list is None:
            logger.warn("Querrying all privileges")
            privilege_list = await ProjectPrivilege.find_all().to_list()

        privilege = next(
            (
                p
                for p in privilege_list
                if p.user.ref.id == user.id and p.project.ref.id == project.id
            ),
            None,
        )

        privilege_level = (
            privilege.level
            if privilege is not None
            else ProjectPrivilegeLevel.GUEST
            if project.is_public
            else ProjectPrivilegeLevel.UNAUTHORIZED
        )

        return privilege_level


project_repo = ProjectRepository()
