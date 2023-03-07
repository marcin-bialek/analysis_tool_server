from fastapi_users.router import (
    get_auth_router,
    get_register_router,
    get_reset_password_router,
    get_users_router,
    get_verify_router,
)

from .manager import get_user_manager
from .schemas import User, UserCreate, UserUpdate
from .users import auth_backend, fastapi_users

# /login and /logout routes
auth_router = get_auth_router(
    auth_backend, get_user_manager, fastapi_users.authenticator
)

# /register route
register_router = get_register_router(get_user_manager, User, UserCreate)

# /forgot-password and /reset-password routes
reset_password_router = get_reset_password_router(get_user_manager)

# /request-verify-token and /verify routes
verify_router = get_verify_router(get_user_manager, User)

# /me and /{user_id} routes
users_router = get_users_router(
    get_user_manager, User, UserUpdate, fastapi_users.authenticator
)
