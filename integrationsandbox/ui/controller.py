import json
import logging
from typing import Annotated, List, Optional, Tuple

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError as PydanticValidationError

from integrationsandbox.broker import service as broker_service
from integrationsandbox.broker.models import (
    BrokerEventFilters,
    BrokerEventMessage,
    BrokerEventType,
)
from integrationsandbox.common.exceptions import ValidationError
from integrationsandbox.config import get_settings
from integrationsandbox.security.models import User
from integrationsandbox.security.service import get_user_from_token, login_user
from integrationsandbox.tms import service as tms_service
from integrationsandbox.tms.models import (
    StopType,
    TmsShipment,
    TmsShipmentFilters,
    TmsStop,
)
from integrationsandbox.trigger import service as trigger_service
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger
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


def _stop_by_type(shipment: TmsShipment, stop_type: StopType) -> Optional[TmsStop]:
    return next((stop for stop in shipment.stops if stop.type == stop_type), None)


def _format_location(stop: Optional[TmsStop]) -> str:
    if stop is None:
        return "—"
    location = stop.location
    if location.address:
        return f"{location.name}, {location.address.city}"
    return location.name or location.code


def _format_stop_datetime(stop: Optional[TmsStop]) -> str:
    if stop is None:
        return "—"
    start = stop.planned_time_window_start.strftime("%H:%M")
    end = stop.planned_time_window_end.strftime("%H:%M")
    return f"{stop.planned_date.isoformat()} {start} - {end}"


def build_shipment_rows(
    shipments_with_status: List[Tuple[TmsShipment, Optional[str]]],
) -> List[dict]:
    rows = []
    for shipment, processed_at in shipments_with_status:
        pickup = _stop_by_type(shipment, StopType.PICKUP)
        delivery = _stop_by_type(shipment, StopType.DELIVERY)
        rows.append(
            {
                "id": shipment.id,
                "status_label": processed_at or "New",
                "is_new": processed_at is None,
                "customer_name": shipment.customer.name,
                "carrier_name": shipment.customer.carrier,
                "pickup_location": _format_location(pickup),
                "pickup_date": _format_stop_datetime(pickup),
                "dropoff_location": _format_location(delivery),
                "dropoff_date": _format_stop_datetime(delivery),
                "pretty_json": json.dumps(shipment.model_dump(mode="json"), indent=2),
            }
        )
    return rows


def shipments_table_context() -> dict:
    filters = TmsShipmentFilters(limit=settings.max_bulk_size)
    shipments_with_status = tms_service.list_shipments_with_status(filters)
    return {"shipments": build_shipment_rows(shipments_with_status)}


def build_event_rows(
    events_with_status: List[Tuple[BrokerEventMessage, Optional[str]]],
) -> List[dict]:
    rows = []
    for event, processed_at in events_with_status:
        rows.append(
            {
                "id": event.id,
                "shipment_id": event.shipmentId,
                "event_type": event.situation.event.value,
                "status_label": processed_at or "New",
                "is_new": processed_at is None,
                "pretty_json": json.dumps(event.model_dump(mode="json"), indent=2),
            }
        )
    return rows


def events_table_context() -> dict:
    filters = BrokerEventFilters(limit=settings.max_bulk_size)
    events_with_status = broker_service.list_events_with_status(filters)
    return {"events": build_event_rows(events_with_status)}


@router.get("/")
async def dashboard(request: Request, user: Annotated[User, Depends(require_ui_user)]):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "event_types": list(BrokerEventType),
            **shipments_table_context(),
            **events_table_context(),
        },
    )


@router.post("/shipments/seed")
async def seed_shipments(
    request: Request,
    user: Annotated[User, Depends(require_ui_user)],
    count: Annotated[int, Form()],
):
    try:
        tms_service.create_seed_shipments(count)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
    return templates.TemplateResponse(
        request, "partials/shipments_table.html", shipments_table_context()
    )


@router.post("/shipments/trigger")
async def trigger_shipments(
    request: Request,
    user: Annotated[User, Depends(require_ui_user)],
    count: Annotated[int, Form()],
    target_url: Annotated[Optional[str], Form()] = None,
):
    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="target_url is required to trigger shipments",
        )
    try:
        trigger = ShipmentTrigger(target_url=target_url, count=count)
    except PydanticValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    trigger_service.create_and_dispatch_shipments(trigger)
    return templates.TemplateResponse(
        request, "partials/shipments_table.html", shipments_table_context()
    )


@router.post("/events/seed")
async def seed_events(
    request: Request,
    user: Annotated[User, Depends(require_ui_user)],
    event_type: Annotated[BrokerEventType, Form()],
    shipment_ids: Annotated[List[str], Form(default_factory=list)],
):
    if not shipment_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Select at least one shipment",
        )
    shipments = tms_service.get_shipments_by_id_list(shipment_ids)
    broker_service.create_seed_events(shipments, event_type)
    return templates.TemplateResponse(
        request, "partials/events_table.html", events_table_context()
    )


@router.post("/events/trigger")
async def trigger_events(
    request: Request,
    user: Annotated[User, Depends(require_ui_user)],
    event_type: Annotated[BrokerEventType, Form()],
    shipment_ids: Annotated[List[str], Form(default_factory=list)],
    target_url: Annotated[Optional[str], Form()] = None,
):
    if not shipment_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Select at least one shipment",
        )
    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="target_url is required to trigger events",
        )
    try:
        trigger = EventTrigger(
            target_url=target_url, event=event_type, shipment_ids=shipment_ids
        )
    except PydanticValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    trigger_service.create_and_dispatch_events(trigger)
    return templates.TemplateResponse(
        request, "partials/events_table.html", events_table_context()
    )
