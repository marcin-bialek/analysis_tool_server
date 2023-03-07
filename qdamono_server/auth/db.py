from fastapi_users.db import BeanieUserDatabase
from fastapi_users_db_beanie.access_token import BeanieAccessTokenDatabase

from .models import AccessToken, User


async def yield_user_db():
    yield BeanieUserDatabase(User)


def get_user_db():
    return BeanieUserDatabase(User)


async def yield_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)


def get_access_token_db():
    return BeanieAccessTokenDatabase(AccessToken)
