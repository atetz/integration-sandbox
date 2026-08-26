from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

from integrationsandbox.broker.models import BrokerEventFilters, BrokerEventType
from integrationsandbox.broker.service import list_events_with_status
from integrationsandbox.config import get_settings
from integrationsandbox.main import app
from integrationsandbox.tms.models import TmsShipmentFilters
from integrationsandbox.tms.service import list_shipments_with_status

settings = get_settings()


@pytest.fixture
def client():
    """A fresh client per test so cookies don't leak between tests.

    Uses an https:// base URL so the Secure ui_session cookie (secure=True
    by default) is actually sent back on subsequent requests.
    """
    return TestClient(app, base_url="https://testserver")


@pytest.fixture
def authenticated_client(client):
    client.post(
        "/ui/login",
        data={
            "username": settings.default_user,
            "password": settings.default_password,
        },
    )
    return client


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


def test_dashboard_lists_shipments_with_status_badges(
    authenticated_client, persisted_shipments, persisted_processed_shipments
):
    response = authenticated_client.get("/ui/")

    assert response.status_code == 200
    for shipment in persisted_shipments:
        assert shipment.id in response.text
    for shipment in persisted_processed_shipments:
        assert shipment.id in response.text
    assert "New" in response.text


def test_dashboard_shows_processed_timestamp_badge(
    authenticated_client, persisted_processed_shipments
):
    response = authenticated_client.get("/ui/")

    assert response.status_code == 200
    shipments = list_shipments_with_status(TmsShipmentFilters(limit=10))
    for _, processed_at in shipments:
        assert processed_at in response.text


def test_seed_endpoint_creates_shipments_and_updates_table(authenticated_client):
    response = authenticated_client.post("/ui/shipments/seed", data={"count": 2})

    assert response.status_code == 200
    shipments = list_shipments_with_status(TmsShipmentFilters(limit=10))
    assert len(shipments) == 2
    for shipment, _ in shipments:
        assert shipment.id in response.text
    assert response.text.count('badge-info">New</span>') == 2


@patch("integrationsandbox.trigger.service.httpx.post")
def test_seed_endpoint_ignores_target_url(mock_post, authenticated_client):
    response = authenticated_client.post(
        "/ui/shipments/seed",
        data={"count": 1, "target_url": "https://example.com/webhook"},
    )

    assert response.status_code == 200
    mock_post.assert_not_called()


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_endpoint_dispatches_shipments_and_updates_table(
    mock_post, authenticated_client
):
    mock_post.return_value.status_code = 200
    target_url = "https://example.com/webhook"

    response = authenticated_client.post(
        "/ui/shipments/trigger", data={"count": 2, "target_url": target_url}
    )

    assert response.status_code == 200
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == target_url
    assert len(kwargs["json"]) == 2

    shipments = list_shipments_with_status(TmsShipmentFilters(limit=10))
    assert len(shipments) == 2
    for shipment, _ in shipments:
        assert shipment.id in response.text


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_endpoint_without_target_url_is_rejected(
    mock_post, authenticated_client
):
    response = authenticated_client.post("/ui/shipments/trigger", data={"count": 1})

    assert response.status_code == 422
    mock_post.assert_not_called()
    assert list_shipments_with_status(TmsShipmentFilters(limit=10)) == []


def test_dashboard_lists_events_with_status_badges(
    authenticated_client, persisted_broker_events
):
    response = authenticated_client.get("/ui/")

    assert response.status_code == 200
    for event in persisted_broker_events:
        assert event.id in response.text
    assert "New" in response.text


def test_seed_events_endpoint_creates_events_for_selected_shipments(
    authenticated_client, persisted_shipments
):
    shipment_ids = [shipment.id for shipment in persisted_shipments]

    response = authenticated_client.post(
        "/ui/events/seed",
        data={
            "shipment_ids": shipment_ids,
            "event_type": BrokerEventType.ORDER_CREATED.value,
        },
    )

    assert response.status_code == 200
    events = list_events_with_status(BrokerEventFilters(limit=10))
    assert len(events) == len(shipment_ids)
    for event, _ in events:
        assert event.id in response.text
    assert response.text.count('badge-info">New</span>') == len(shipment_ids)


def test_seed_events_endpoint_without_shipment_ids_is_rejected(authenticated_client):
    response = authenticated_client.post(
        "/ui/events/seed", data={"event_type": BrokerEventType.ORDER_CREATED.value}
    )

    assert response.status_code == 422
    assert list_events_with_status(BrokerEventFilters(limit=10)) == []


def test_seed_events_endpoint_with_unknown_shipment_id_is_rejected(
    authenticated_client,
):
    response = authenticated_client.post(
        "/ui/events/seed",
        data={
            "shipment_ids": ["does-not-exist"],
            "event_type": BrokerEventType.ORDER_CREATED.value,
        },
    )

    assert response.status_code == 422
    assert list_events_with_status(BrokerEventFilters(limit=10)) == []


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_events_endpoint_dispatches_events_and_updates_table(
    mock_post, authenticated_client, persisted_shipments
):
    mock_post.return_value.status_code = 200
    shipment_ids = [shipment.id for shipment in persisted_shipments]
    target_url = "https://example.com/webhook"

    response = authenticated_client.post(
        "/ui/events/trigger",
        data={
            "shipment_ids": shipment_ids,
            "event_type": BrokerEventType.ORDER_CREATED.value,
            "target_url": target_url,
        },
    )

    assert response.status_code == 200
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == target_url
    assert len(kwargs["json"]) == len(shipment_ids)

    events = list_events_with_status(BrokerEventFilters(limit=10))
    assert len(events) == len(shipment_ids)
    for event, _ in events:
        assert event.id in response.text


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_events_endpoint_without_target_url_is_rejected(
    mock_post, authenticated_client, persisted_shipments
):
    shipment_ids = [shipment.id for shipment in persisted_shipments]

    response = authenticated_client.post(
        "/ui/events/trigger",
        data={
            "shipment_ids": shipment_ids,
            "event_type": BrokerEventType.ORDER_CREATED.value,
        },
    )

    assert response.status_code == 422
    mock_post.assert_not_called()
    assert list_events_with_status(BrokerEventFilters(limit=10)) == []


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_events_endpoint_without_shipment_ids_is_rejected(
    mock_post, authenticated_client
):
    response = authenticated_client.post(
        "/ui/events/trigger",
        data={
            "event_type": BrokerEventType.ORDER_CREATED.value,
            "target_url": "https://example.com/webhook",
        },
    )

    assert response.status_code == 422
    mock_post.assert_not_called()
    assert list_events_with_status(BrokerEventFilters(limit=10)) == []


@patch("integrationsandbox.trigger.service.httpx.post")
def test_trigger_events_endpoint_with_unknown_shipment_id_is_rejected(
    mock_post, authenticated_client
):
    response = authenticated_client.post(
        "/ui/events/trigger",
        data={
            "shipment_ids": ["does-not-exist"],
            "event_type": BrokerEventType.ORDER_CREATED.value,
            "target_url": "https://example.com/webhook",
        },
    )

    assert response.status_code == 422
    mock_post.assert_not_called()
    assert list_events_with_status(BrokerEventFilters(limit=10)) == []
