import os

from a2a.server.apps.jsonrpc import A2AFastAPIApplication
from fastapi import FastAPI

from app.a2a_handler import TravelRequestHandler, build_agent_card
from app.core.config import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    base_url = os.getenv("AGENT_PUBLIC_URL", "http://localhost:8000").rstrip("/")

    handler = TravelRequestHandler(settings=settings, base_url=base_url)
    agent_card = build_agent_card(base_url)

    application = A2AFastAPIApplication(agent_card=agent_card, http_handler=handler)
    app = application.build(rpc_url="/a2a")

    @app.get("/healthz")
    def health() -> dict:
        return {"status": "ok"}

    app.state.settings = settings
    app.state.agent_card = agent_card
    return app
