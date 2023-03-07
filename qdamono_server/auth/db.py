from fastapi_users.db import BeanieUserDatabase
from fastapi_users_db_beanie.access_token import BeanieAccessTokenDatabase

from .models import AccessToken, User


async def get_user_db():
    yield BeanieUserDatabase(User)


async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)
