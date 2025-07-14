from fastapi import FastAPI

from integrationsandbox.infrastructure.database import setup
from integrationsandbox.trigger import controller

app = FastAPI()
app.include_router(controller.router)


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
