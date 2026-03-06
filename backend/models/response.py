"""Response models for API endpoints."""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of streaming messages."""

    THINKING = "thinking"
    CODE = "code"
    EXECUTION = "execution"
    RESULT = "result"
    ERROR = "error"
    DONE = "done"


class StreamMessage(BaseModel):
    """Streaming message from agent execution."""

    type: MessageType = Field(..., description="Type of message")
    content: str | dict[str, Any] = Field(..., description="Message content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExecutionResult(BaseModel):
    """Result of code execution in sandbox."""

    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    error: str | None = Field(default=None, description="Error message if any")
    results: list[Any] = Field(default_factory=list, description="Execution results (charts, dataframes, etc.)")
    exit_code: int = Field(default=0, description="Exit code")


class ChatResponse(BaseModel):
    """Response model for chat messages."""

    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session identifier")
    execution_result: ExecutionResult | None = Field(default=None, description="Code execution result if any")


class SandboxResponse(BaseModel):
    """Response model for sandbox operations."""

    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Sandbox status")
    message: str = Field(default="", description="Status message")
