from contextlib import asynccontextmanager

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware

from integrationsandbox.broker import controller as broker_controller
from integrationsandbox.common.exceptions import NotFoundError, ValidationError
from integrationsandbox.config import get_settings
from integrationsandbox.infrastructure import database
from integrationsandbox.infrastructure.exceptions import RepositoryError
from integrationsandbox.tms import controller as tms_controller
from integrationsandbox.trigger import controller as trigger_controller

APP_TITLE = "Integration Sandbox"
APP_DESCRIPTION = "API for integration sandbox services"
APP_VERSION = "1.0.0"

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.setup()
    yield
    pass


app = FastAPI(
    lifespan=lifespan,
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# CORS configuration
settings = get_settings()
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


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return responses.JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return responses.JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(RepositoryError)
async def repository_error_handler(request, exc):
    return responses.JSONResponse(status_code=500, content={"detail": str(exc)})
