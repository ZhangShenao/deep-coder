"""Chat API routes."""
import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from backend.agent import get_coding_agent
from backend.models import ChatRequest, ChatResponse, ExecutionResult, MessageType
from backend.sandbox import get_sandbox_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the coding agent.

    Args:
        request: Chat request with message and session_id

    Returns:
        Agent response with optional execution results
    """
    try:
        sandbox_manager = get_sandbox_manager()

        # Ensure sandbox exists
        sandbox = await sandbox_manager.get_sandbox(request.session_id)
        if not sandbox:
            sandbox = await sandbox_manager.create_sandbox(request.session_id)

        # Create agent with sandbox context
        agent = get_coding_agent()
        agent.set_sandbox_tools({
            "execute": lambda code: sandbox.run_code(code),
            "write_file": lambda path, content: sandbox.files.write(path, content),
            "read_file": lambda path: sandbox.files.read(path),
            "list_files": lambda path: sandbox.files.list(path),
        })

        # Invoke agent
        result = await agent.ainvoke(request.message, request.session_id)

        # Extract response
        if "messages" in result:
            response_text = result["messages"][-1].content if result["messages"] else ""
        else:
            response_text = result.get("output", str(result))

        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            execution_result=None,
        )

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat.

    Provides streaming responses and execution updates.

    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier
    """
    await websocket.accept()
    sandbox_manager = get_sandbox_manager()

    try:
        # Create sandbox for this session
        sandbox = await sandbox_manager.get_sandbox(session_id)
        if not sandbox:
            sandbox = await sandbox_manager.create_sandbox(session_id)

        while True:
            # Receive message
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
            except json.JSONDecodeError:
                user_message = data

            try:
                # Send thinking status
                await websocket.send_json({
                    "type": MessageType.THINKING.value,
                    "content": "Processing your request...",
                })

                # Create agent with sandbox context
                agent = get_coding_agent()
                agent.set_sandbox_tools({
                    "execute": lambda code: sandbox.run_code(code),
                    "write_file": lambda path, content: sandbox.files.write(path, content),
                    "read_file": lambda path: sandbox.files.read(path),
                    "list_files": lambda path: sandbox.files.list(path),
                })

                # Stream agent response
                full_response = ""
                async for event in agent.astream(user_message, session_id):
                    # Handle different event types
                    if isinstance(event, dict):
                        if "messages" in event:
                            messages = event["messages"]
                            if messages:
                                last_msg = messages[-1]
                                content = getattr(last_msg, "content", str(last_msg))

                                # Send code blocks separately
                                if "```" in content and content != full_response:
                                    full_response = content
                                    await websocket.send_json({
                                        "type": MessageType.CODE.value,
                                        "content": content,
                                    })

                        # Check for tool calls (code execution)
                        if "intermediate_steps" in event:
                            for step in event["intermediate_steps"]:
                                if hasattr(step, "tool") and step.tool == "execute_code":
                                    await websocket.send_json({
                                        "type": MessageType.EXECUTION.value,
                                        "content": "Executing code in sandbox...",
                                    })

                # Send final response
                await websocket.send_json({
                    "type": MessageType.RESULT.value,
                    "content": full_response or "Task completed",
                })

                # Send done signal
                await websocket.send_json({
                    "type": MessageType.DONE.value,
                    "content": "",
                })

            except Exception as e:
                logger.error(f"Error in agent processing: {e}")
                await websocket.send_json({
                    "type": MessageType.ERROR.value,
                    "content": str(e),
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Optionally destroy sandbox on disconnect
        # await sandbox_manager.destroy_sandbox(session_id)
        pass
