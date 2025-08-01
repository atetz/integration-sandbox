import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from integrationsandbox.config import get_settings
from integrationsandbox.security import repository
from integrationsandbox.security.models import Token, TokenData, User

settings = get_settings()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate_user(username: str, password: str):
    logger.debug("Authenticating user: %s", username)
    user = repository.get_user(username)
    if not user:
        logger.debug("User not found: %s", username)
        return False
    if not verify_password(password, user.hashed_password):
        logger.debug("Invalid password for user: %s", username)
        return False
    logger.debug("Authentication successful for user: %s", username)
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    logger.debug("Creating access token for data: %s", data)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    logger.debug("Access token created successfully")
    return encoded_jwt


def login_user(username: str, password: str) -> Token | None:
    logger.info("Processing login for user: %s", username)
    user = authenticate_user(username, password)
    if not user:
        logger.info("Login failed for user: %s", username)
        return None

    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info("Login token created for user: %s", username)
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    logger.debug("Validating JWT token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username = payload.get("sub")
        if username is None:
            logger.debug("Token missing username")
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.debug("Token validated for user: %s", username)
    except InvalidTokenError:
        logger.debug("Invalid JWT token")
        raise credentials_exception
    user = repository.get_user(username=token_data.username)
    if user is None:
        logger.debug("Token user not found: %s", token_data.username)
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    logger.debug("Checking if user is active: %s", current_user.username)
    if current_user.disabled:
        logger.warning("Inactive user attempted access: %s", current_user.username)
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
