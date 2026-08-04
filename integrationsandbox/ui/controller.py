import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from integrationsandbox.config import get_settings
from integrationsandbox.security.models import User
from integrationsandbox.security.service import get_user_from_token, login_user
from integrationsandbox.ui.exceptions import UIAuthenticationRequired

router = APIRouter(prefix="/ui", tags=["UI"])
templates = Jinja2Templates(directory="integrationsandbox/ui/templates")
settings = get_settings()
logger = logging.getLogger(__name__)

UI_COOKIE_NAME = "ui_session"


async def require_ui_user(request: Request) -> User:
    token = request.cookies.get(UI_COOKIE_NAME)
    user = get_user_from_token(token) if token else None
    if user is None or user.disabled:
        raise UIAuthenticationRequired()
    return user


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
async def login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    token = login_user(
        username, password, expires_minutes=settings.ui_session_expire_minutes
    )
    if token is None:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=UI_COOKIE_NAME,
        value=token.access_token,
        httponly=True,
        secure=settings.ui_cookie_secure,
        samesite="lax",
        max_age=settings.ui_session_expire_minutes * 60,
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(UI_COOKIE_NAME)
    return response


@router.get("/")
async def dashboard(request: Request, user: Annotated[User, Depends(require_ui_user)]):
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})
