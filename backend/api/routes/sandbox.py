"""Sandbox management API routes."""
import logging

from fastapi import APIRouter, HTTPException

from backend.models import SandboxCreateRequest, SandboxResponse
from backend.sandbox import get_sandbox_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=SandboxResponse)
async def create_sandbox(request: SandboxCreateRequest):
    """Create a new sandbox for a session.

    Args:
        request: Sandbox creation request

    Returns:
        Sandbox status response
    """
    try:
        manager = get_sandbox_manager()
        sandbox = await manager.create_sandbox(
            session_id=request.session_id,
            timeout=request.timeout,
        )

        return SandboxResponse(
            session_id=request.session_id,
            status="created",
            message="Sandbox created successfully",
        )

    except Exception as e:
        logger.error(f"Error creating sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", response_model=SandboxResponse)
async def destroy_sandbox(session_id: str):
    """Destroy a sandbox.

    Args:
        session_id: Session identifier

    Returns:
        Sandbox status response
    """
    try:
        manager = get_sandbox_manager()
        destroyed = await manager.destroy_sandbox(session_id)

        if destroyed:
            return SandboxResponse(
                session_id=session_id,
                status="destroyed",
                message="Sandbox destroyed successfully",
            )
        else:
            return SandboxResponse(
                session_id=session_id,
                status="not_found",
                message="No sandbox found for this session",
            )

    except Exception as e:
        logger.error(f"Error destroying sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/status", response_model=SandboxResponse)
async def get_sandbox_status(session_id: str):
    """Get sandbox status.

    Args:
        session_id: Session identifier

    Returns:
        Sandbox status response
    """
    try:
        manager = get_sandbox_manager()
        sandbox = await manager.get_sandbox(session_id)

        if sandbox:
            return SandboxResponse(
                session_id=session_id,
                status="active",
                message="Sandbox is running",
            )
        else:
            return SandboxResponse(
                session_id=session_id,
                status="not_found",
                message="No sandbox found for this session",
            )

    except Exception as e:
        logger.error(f"Error getting sandbox status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
