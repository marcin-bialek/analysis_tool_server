from logging import getLogger
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from password_strength import PasswordPolicy, PasswordStats, tests, tests_base

from qdamono_server.settings import settings

from .db import get_user_db, yield_user_db
from .models import User

logger = getLogger(__name__)


class PasswordRestrictions:
    MIN_LENGTH = 8
    MAX_LENGTH = 32
    MIN_LOWERCASE = 1
    MIN_UPPERCASE = 1
    MIN_DIGITS = 1
    MIN_SPECIAL = 1

    class MaxLength(tests_base.ATest):
        """Tests whether password length <= `length`"""

        def __init__(self, length: int):
            super(PasswordRestrictions.MaxLength, self).__init__(length)
            self.length = length

        def test(self, ps: PasswordStats):
            return ps.length <= self.length

    class Lowercase(tests_base.ATest):
        """Test whether the password has >= `count` lowercase characters"""

        def __init__(self, count: int):
            super(PasswordRestrictions.Lowercase, self).__init__(count)
            self.count = count

        def test(self, ps: PasswordStats):
            return ps.letters_lowercase >= self.count

    class Email(tests_base.ATest):
        """Test whether the password contains user's email"""

        def __init__(self, email: str):
            super(PasswordRestrictions.Email, self).__init__(email)
            self.email = email

        def test(self, ps: PasswordStats):
            return self.email not in ps.password


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.auth_key
    verification_token_secret = settings.auth_key

    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        logger.warn(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )

    async def on_after_login(self, user: User, request: Request | None = None) -> None:
        logger.info(f"User {user.id} has logged in.")

    async def on_after_verify(self, user: User, request: Request | None = None) -> None:
        logger.info(f"User {user.id} has been verified.")

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ) -> None:
        logger.warn(f"User {user.id} has reset their password.")

    async def on_before_delete(
        self, user: User, request: Request | None = None
    ) -> None:
        logger.warn(f"User {user.id} is going to be deleted.")

    async def on_after_delete(self, user: User, request: Request | None = None) -> None:
        logger.info(f"User {user.id} has been deleted.")

    async def validate_password(self, password: str, user: User) -> None:
        policy = PasswordPolicy.from_names(
            length=PasswordRestrictions.MIN_LENGTH,
            maxlength=PasswordRestrictions.MAX_LENGTH,
            uppercase=PasswordRestrictions.MIN_UPPERCASE,
            lowercase=PasswordRestrictions.MIN_LOWERCASE,
            numbers=PasswordRestrictions.MIN_DIGITS,
            special=PasswordRestrictions.MIN_SPECIAL,
        )

        failed_tests: list[tests_base.ATest] = policy.test(password)

        if len(failed_tests) >= 1:
            messages: list[str] = []

            for failed_test in failed_tests:
                if isinstance(failed_test, tests.Length):
                    messages.append(f"at least {PasswordRestrictions.MIN_LENGTH} long")
                elif isinstance(failed_test, PasswordRestrictions.MaxLength):
                    messages.append(
                        f"less than {PasswordRestrictions.MAX_LENGTH} characters long"
                    )
                elif isinstance(failed_test, tests.Uppercase):
                    messages.append(
                        f"at least {PasswordRestrictions.MIN_UPPERCASE} uppercase letter{'s' if PasswordRestrictions.MIN_UPPERCASE > 1 else ''}"
                    )
                elif isinstance(failed_test, PasswordRestrictions.Lowercase):
                    messages.append(
                        f"at least {PasswordRestrictions.MIN_UPPERCASE} uppercase letters{'s' if PasswordRestrictions.MIN_UPPERCASE > 1 else ''}"
                    )
                elif isinstance(failed_test, tests.Numbers):
                    messages.append(
                        f"at least {PasswordRestrictions.MIN_DIGITS} digit{'s' if PasswordRestrictions.MIN_DIGITS > 1 else ''}"
                    )
                elif isinstance(failed_test, tests.Special):
                    messages.append(
                        f"at least {PasswordRestrictions.MIN_SPECIAL} special characters"
                    )
                elif isinstance(failed_test, PasswordRestrictions.Email):
                    messages.append("password should not contain email")

            raise InvalidPasswordException(
                f"Password failed check{'s' if len(messages) > 1 else ''}: {', '.join(messages)}"
            )


async def yield_user_manager(user_db=Depends(yield_user_db)):
    yield UserManager(user_db)


def get_user_manager():
    return UserManager(get_user_db())
