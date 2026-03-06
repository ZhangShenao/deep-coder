"""Deep-Coder Streamlit Frontend Application."""

import asyncio
import json
import os
import uuid

import httpx
import streamlit as st

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WS_URL = BACKEND_URL.replace("http", "ws")


def init_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = ""
    if "execution_logs" not in st.session_state:
        st.session_state.execution_logs = []


def render_sidebar():
    """Render the sidebar with session info and controls."""
    with st.sidebar:
        st.header("Session Info")
        st.text_input(
            "Session ID",
            value=st.session_state.session_id[:8] + "...",
            disabled=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("New Session", use_container_width=True):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.session_state.generated_code = ""
                st.session_state.execution_logs = []
                st.rerun()

        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.generated_code = ""
                st.session_state.execution_logs = []
                st.rerun()

        st.divider()

        # API Configuration
        st.header("Configuration")
        backend_url = st.text_input(
            "Backend URL",
            value=BACKEND_URL,
            key="backend_url_input",
        )

        st.divider()

        # Status
        st.header("Status")
        try:
            with httpx.Client() as client:
                response = client.get(f"{backend_url}/health", timeout=2.0)
                if response.status_code == 200:
                    st.success("Backend: Connected")
                else:
                    st.error("Backend: Error")
        except Exception:
            st.error("Backend: Disconnected")


def render_chat_panel():
    """Render the chat panel."""
    st.subheader("Chat")

    # Display chat messages
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

                # Show code blocks if present
                if "code" in msg:
                    with st.expander("Generated Code", expanded=False):
                        st.code(msg["code"], language="python")


def render_code_panel():
    """Render the code display panel."""
    st.subheader("Generated Code")

    if st.session_state.generated_code:
        st.code(st.session_state.generated_code, language="python")

        # Copy button
        if st.button("Copy Code"):
            st.clipboard(st.session_state.generated_code)
            st.toast("Code copied!")
    else:
        st.info("Code will appear here when generated")


def render_results_panel():
    """Render the execution results panel."""
    st.subheader("Execution Results")

    if st.session_state.execution_logs:
        for log in st.session_state.execution_logs:
            if log["type"] == "error":
                st.error(log["content"])
            elif log["type"] == "execution":
                st.info(log["content"])
            else:
                st.text(log["content"])
    else:
        st.info("Execution logs will appear here")


async def send_message_async(message: str) -> None:
    """Send message via WebSocket and handle streaming response."""
    import websockets

    ws_url = f"{WS_URL}/api/chat/ws/{st.session_state.session_id}"

    try:
        async with websockets.connect(ws_url) as websocket:
            # Send message
            await websocket.send(json.dumps({"message": message}))

            # Receive streaming responses
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)

                    msg_type = data.get("type", "")
                    content = data.get("content", "")

                    if msg_type == "thinking":
                        st.session_state.execution_logs.append(
                            {
                                "type": "info",
                                "content": content,
                            }
                        )
                    elif msg_type == "code":
                        st.session_state.generated_code = extract_code(content)
                    elif msg_type == "execution":
                        st.session_state.execution_logs.append(
                            {
                                "type": "execution",
                                "content": content,
                            }
                        )
                    elif msg_type == "result":
                        st.session_state.messages[-1]["content"] = content
                    elif msg_type == "error":
                        st.session_state.execution_logs.append(
                            {
                                "type": "error",
                                "content": content,
                            }
                        )
                    elif msg_type == "done":
                        break

                except websockets.exceptions.ConnectionClosed:
                    break

    except Exception as e:
        st.session_state.execution_logs.append(
            {
                "type": "error",
                "content": f"Connection error: {str(e)}",
            }
        )


def send_message_sync(message: str) -> str:
    """Send message via REST API (fallback)."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BACKEND_URL}/api/chat/message",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id,
                },
                timeout=180.0,  # 3 minutes for complex agent operations
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    except Exception as e:
        return f"Error: {str(e)}"


def extract_code(text: str) -> str:
    """Extract code from markdown code blocks."""
    import re

    pattern = r"```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return "\n\n".join(matches)
    return text


def main():
    """Main application."""
    st.set_page_config(
        page_title="Deep-Coder",
        page_icon="🤖",
        layout="wide",
    )

    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("🤖 Deep-Coder")
    st.caption("AI-powered coding assistant")

    # Three-column layout
    col1, col2, col3 = st.columns([1.5, 1, 1])

    with col1:
        render_chat_panel()

        # Chat input
        if prompt := st.chat_input("Describe your coding task..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Send to backend
            with st.spinner("Processing..."):
                try:
                    response = send_message_sync(prompt)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                        }
                    )
                    # Extract code if present
                    code = extract_code(response)
                    if code != response:
                        st.session_state.generated_code = code
                except Exception as e:
                    st.error(f"Error: {e}")

            st.rerun()

    with col2:
        render_code_panel()

    with col3:
        render_results_panel()


if __name__ == "__main__":
    main()
