from uuid import UUID

from fastapi_users_db_beanie.access_token import BeanieBaseAccessToken


class AccessToken(BeanieBaseAccessToken[UUID]):
    pass
