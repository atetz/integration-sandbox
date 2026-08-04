import logging

from fastapi import APIRouter, Depends, status

from integrationsandbox.broker import service as broker_service
from integrationsandbox.security.service import get_current_active_user
from integrationsandbox.tms import service as tms_service

router = APIRouter(dependencies=[Depends(get_current_active_user)], tags=["System"])
logger = logging.getLogger(__name__)


@router.delete(
    "/nuke",
    summary="Nuke the sandbox",
    description="""
      Deletes every TMS shipment and every broker event. Schema and running app are left untouched.
      """,
    response_description="HTTP 204 with no body.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def nuke() -> None:
    logger.info("Nuking sandbox: deleting all TMS shipments and broker events")
    tms_service.delete_all_shipments()
    broker_service.delete_all_events()
    logger.info("Successfully nuked sandbox")
