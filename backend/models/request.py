"""Request models for API endpoints."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat messages."""

    message: str = Field(..., description="User message to the agent")
    session_id: str = Field(..., description="Unique session identifier")


class SandboxCreateRequest(BaseModel):
    """Request model for creating a sandbox."""

    session_id: str = Field(..., description="Session to associate with sandbox")
    timeout: int = Field(default=300, description="Sandbox timeout in seconds")
