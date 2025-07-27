from contextlib import asynccontextmanager

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware

from integrationsandbox.broker import controller as broker_controller
from integrationsandbox.common.exceptions import ValidationError
from integrationsandbox.infrastructure import database
from integrationsandbox.infrastructure.exceptions import RepositoryError
from integrationsandbox.tms import controller as tms_controller
from integrationsandbox.trigger import controller as trigger_controller

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database.setup()
    yield
    # Shutdown: Add any cleanup code here if needed
    pass


app = FastAPI(
    lifespan=lifespan,
    title="Integration Sandbox",
    description="API for integration sandbox services",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.exception_handler(RepositoryError)
async def repository_error_handler(request, exc):
    return responses.JSONResponse(status_code=500, content={"detail": str(exc)})
