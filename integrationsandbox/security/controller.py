import base64
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param

from integrationsandbox.security.models import Token, User
from integrationsandbox.security.service import get_current_active_user, login_user

from .security import OAuth2TokenRequestForm

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)

"""
 using the client_id and client_secret option as a front to username and password. 
 For the sandbox to support both is fine. This is by no means a correct implementation of client grant.
 /token will support form data method and basic auth method for OAuth 2.1 compliance.
 """


@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2TokenRequestForm, Depends()],
) -> Token:
    auth_username = None
    auth_password = None

    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme.lower() == "basic":
            try:
                decoded = base64.b64decode(credentials).decode("utf-8")
                auth_username, auth_password = decoded.split(":", 1)
            except (ValueError, UnicodeDecodeError):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header",
                    headers={"WWW-Authenticate": "Basic"},
                )

    if form_data.grant_type == "client_credentials":
        username = auth_username or form_data.client_id
        password = auth_password or form_data.client_secret

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Client credentials required",
                headers={"WWW-Authenticate": "Basic"},
            )

        logger.info("Login attempt for client_credentials: %s", username)
        token = login_user(username, password)

    elif form_data.grant_type == "password":
        username = form_data.username
        password = form_data.password

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password required",
            )

        logger.info("Login attempt for password grant: %s", username)
        token = login_user(username, password)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant_type: {form_data.grant_type}",
        )

    if not token:
        logger.warning("Login failed for %s: %s", form_data.grant_type, username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info("Login successful for %s: %s", form_data.grant_type, username)
    return token


@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    logger.info("User profile requested for: %s", current_user.username)
    return current_user
