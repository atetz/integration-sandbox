import bcrypt

from integrationsandbox.config import get_settings
from integrationsandbox.security.models import UserInDB


def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_users_db():
    settings = get_settings()
    return {
        settings.default_user: {
            "username": settings.default_user,
            "hashed_password": get_password_hash(settings.default_password),
            "disabled": False,
        }
    }


def get_user(username: str):
    db = get_users_db()
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
