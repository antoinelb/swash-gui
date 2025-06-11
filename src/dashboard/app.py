from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from .api import routes

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"
INDEX_PATH = STATIC_DIR / "index.html"


async def serve_spa(request):
    """Serve index.html for all non-API routes (SPA routing)."""
    return FileResponse(INDEX_PATH)


def create_app() -> Starlette:
    """Create and configure the Starlette application."""
    # Define static file routes
    static_routes = [
        Mount("/css", app=StaticFiles(directory=str(STATIC_DIR / "css"))),
        Mount("/js", app=StaticFiles(directory=str(STATIC_DIR / "js"))),
        Mount(
            "/assets", app=StaticFiles(directory=str(STATIC_DIR / "assets"))
        ),
    ]

    app = Starlette(
        debug=True,
        routes=[
            Mount("/api", routes=routes.get_api_routes()),
            *static_routes,
            # Catch-all route for SPA - must be last
            Route("/{path:path}", serve_spa),
            Route("/", serve_spa),
        ],
    )

    # Add CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the dashboard server."""
    uvicorn.run(
        "src.dashboard.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent.parent)],
    )


if __name__ == "__main__":
    run_server()
