"""FastAPI application factory for OpenRFP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from openrfp.api.routes import router
from openrfp.config import settings
from openrfp.web.ui import get_dashboard_html


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="OpenRFP Agent",
        description="Autonomous B2B RFP & Proposal Response Agent API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/", response_class=HTMLResponse, tags=["Dashboard UI"])
    def serve_dashboard() -> HTMLResponse:
        """Serve the OpenRFP interactive dashboard UI."""
        return HTMLResponse(content=get_dashboard_html())

    return app


app = create_app()
