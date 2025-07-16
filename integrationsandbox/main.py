from fastapi import FastAPI

from integrationsandbox.infrastructure import database
from integrationsandbox.trigger import controller

app = FastAPI()
app.include_router(controller.router)


database.setup()
