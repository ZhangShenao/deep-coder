"""API client for backend communication."""
import httpx


class APIClient:
    """Client for communicating with the Deep-Coder backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=60.0)

    def __del__(self):
        self.client.close()

    def send_message(self, message: str, session_id: str) -> dict:
        """Send a chat message to the agent.

        Args:
            message: User message
            session_id: Session identifier

        Returns:
            Response dict with agent reply
        """
        response = self.client.post(
            f"{self.base_url}/api/chat/message",
            json={"message": message, "session_id": session_id},
        )
        response.raise_for_status()
        return response.json()

    def create_session(self) -> str:
        """Create a new session.

        Returns:
            New session ID
        """
        response = self.client.post(f"{self.base_url}/api/session/create")
        response.raise_for_status()
        return response.json()["session_id"]

    def create_sandbox(self, session_id: str, timeout: int = 300) -> dict:
        """Create a sandbox for a session.

        Args:
            session_id: Session identifier
            timeout: Sandbox timeout in seconds

        Returns:
            Response dict
        """
        response = self.client.post(
            f"{self.base_url}/api/sandbox/create",
            json={"session_id": session_id, "timeout": timeout},
        )
        response.raise_for_status()
        return response.json()

    def destroy_sandbox(self, session_id: str) -> dict:
        """Destroy a sandbox.

        Args:
            session_id: Session identifier

        Returns:
            Response dict
        """
        response = self.client.delete(f"{self.base_url}/api/sandbox/{session_id}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check backend health.

        Returns:
            True if healthy
        """
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
