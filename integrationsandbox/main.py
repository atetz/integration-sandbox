import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware

from integrationsandbox.broker import controller as broker_controller
from integrationsandbox.common.exceptions import NotFoundError, ValidationError
from integrationsandbox.config import get_settings, tags_metadata
from integrationsandbox.infrastructure import database
from integrationsandbox.infrastructure.exceptions import RepositoryError
from integrationsandbox.security import controller as security_controller
from integrationsandbox.tms import controller as tms_controller
from integrationsandbox.trigger import controller as trigger_controller

APP_TITLE = "Integration Sandbox"
APP_DESCRIPTION = "API for integration sandbox services"
APP_VERSION = "1.0.0"

API_PREFIX = "/api/v1"
settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.setup()
    dictConfig(settings.log_config)
    yield
    pass


app = FastAPI(
    lifespan=lifespan,
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    openapi_tags=tags_metadata,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(trigger_controller.router, prefix=API_PREFIX)
app.include_router(tms_controller.router, prefix=API_PREFIX)
app.include_router(broker_controller.router, prefix=API_PREFIX)
app.include_router(security_controller.router)


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    logger.exception("Validation error for: %s", request.url)
    return responses.JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    logger.exception("Not found error for: %s", request.url)
    return responses.JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(RepositoryError)
async def repository_error_handler(request, exc):
    logger.exception("Repository error for: %s", request.url)
    return responses.JSONResponse(status_code=500, content={"detail": str(exc)})


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
