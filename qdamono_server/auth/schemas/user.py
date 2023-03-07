from uuid import UUID

from fastapi_users.schemas import BaseUser


class User(BaseUser[UUID]):
    pass
