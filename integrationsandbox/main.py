from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from integrationsandbox.broker import controller as broker_controller
from integrationsandbox.infrastructure import database
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
