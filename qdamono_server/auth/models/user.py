from uuid import UUID, uuid4

from fastapi_users.db import BeanieBaseUser
from pydantic import Field


class User(BeanieBaseUser[UUID]):
    id: UUID = Field(default_factory=uuid4)
