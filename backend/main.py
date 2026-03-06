"""Backend entry point for running with uvicorn."""
import uvicorn

from backend.api import app
from backend.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.api:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
    )
