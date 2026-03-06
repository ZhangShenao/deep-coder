"""Session management API routes."""
import logging
import uuid

from fastapi import APIRouter

from backend.models import SandboxResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
async def create_session():
    """Create a new session.

    Returns:
        New session ID
    """
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "message": "Session created successfully",
    }


@router.get("/{session_id}/info")
async def get_session_info(session_id: str):
    """Get session information.

    Args:
        session_id: Session identifier

    Returns:
        Session information
    """
    return {
        "session_id": session_id,
        "status": "active",
    }
