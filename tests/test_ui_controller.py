from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from integrationsandbox.config import get_settings
from integrationsandbox.main import app

settings = get_settings()


@pytest.fixture
def client():
    """A fresh client per test so cookies don't leak between tests.

    Uses an https:// base URL so the Secure ui_session cookie (secure=True
    by default) is actually sent back on subsequent requests.
    """
    return TestClient(app, base_url="https://testserver")


def test_login_with_valid_credentials_sets_cookie_and_redirects(client):
    response = client.post(
        "/ui/login",
        data={
            "username": settings.default_user,
            "password": settings.default_password,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/ui/"
    assert "ui_session" in response.cookies


def test_login_with_invalid_credentials_shows_error_and_sets_no_cookie(client):
    response = client.post(
        "/ui/login",
        data={"username": settings.default_user, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "ui_session" not in response.cookies
    assert "Invalid username or password" in response.text


def test_dashboard_without_cookie_redirects_to_login(client):
    response = client.get("/ui/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/ui/login"


def test_dashboard_with_invalid_cookie_redirects_to_login(client):
    client.cookies.set("ui_session", "not-a-valid-jwt")

    response = client.get("/ui/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/ui/login"


def test_dashboard_with_expired_cookie_redirects_to_login(client):
    expired_token = jwt.encode(
        {
            "sub": settings.default_user,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    client.cookies.set("ui_session", expired_token)

    response = client.get("/ui/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/ui/login"


def test_dashboard_with_valid_cookie_renders(client):
    client.post(
        "/ui/login",
        data={
            "username": settings.default_user,
            "password": settings.default_password,
        },
    )

    response = client.get("/ui/")

    assert response.status_code == 200
    assert settings.default_user in response.text


def test_logout_clears_cookie_and_subsequent_dashboard_request_redirects(client):
    client.post(
        "/ui/login",
        data={
            "username": settings.default_user,
            "password": settings.default_password,
        },
    )

    logout_response = client.post("/ui/logout", follow_redirects=False)

    assert logout_response.status_code == 303
    assert logout_response.headers["location"] == "/ui/login"

    dashboard_response = client.get("/ui/", follow_redirects=False)

    assert dashboard_response.status_code == 303
    assert dashboard_response.headers["location"] == "/ui/login"
