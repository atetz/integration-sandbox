import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from integrationsandbox.security.models import Token, User
from integrationsandbox.security.service import get_current_active_user, login_user

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    logger.info("Login attempt for user: %s", form_data.username)
    token = login_user(form_data.username, form_data.password)
    if not token:
        logger.warning("Login failed for user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Login successful for user: %s", form_data.username)
    return token


@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    logger.info("User profile requested for: %s", current_user.username)
    return current_user
