"""E2B Sandbox manager for code execution."""
from __future__ import annotations

import logging
from typing import Any

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Try to import E2B, provide mock for development
try:
    from e2b_code_interpreter import AsyncSandbox

    HAS_E2B = True
except ImportError:
    HAS_E2B = False
    logger.warning("E2B not installed. Sandbox features will be limited.")


class MockSandbox:
    """Mock sandbox for development without E2B."""

    def __init__(self):
        self._files: dict[str, str] = {}

    async def run_code(self, code: str) -> Any:
        """Mock code execution."""
        result = type("Result", (), {})()
        result.logs = type("Logs", (), {"stdout": "", "stderr": ""})()
        result.error = None
        result.results = []

        # Simple mock execution
        try:
            local_vars: dict[str, Any] = {}
            exec(code, {"__builtins__": __builtins__}, local_vars)
            if local_vars:
                result.logs.stdout = str(local_vars)
        except Exception as e:
            result.logs.stderr = str(e)
            result.error = str(e)

        return result

    async def files_write(self, path: str, content: str) -> None:
        """Mock file write."""
        self._files[path] = content

    async def files_read(self, path: str) -> str:
        """Mock file read."""
        return self._files.get(path, "")

    async def files_list(self, path: str) -> list:
        """Mock file list."""
        return [f for f in self._files.keys() if f.startswith(path)]

    async def close(self) -> None:
        """Close mock sandbox."""
        pass


class SandboxManager:
    """Manages E2B sandbox instances for code execution."""

    def __init__(self):
        self._sandboxes: dict[str, Any] = {}
        self._settings = get_settings()

    async def create_sandbox(
        self,
        session_id: str,
        timeout: int | None = None,
    ) -> Any:
        """Create a new sandbox instance for a session.

        Args:
            session_id: Unique session identifier
            timeout: Sandbox timeout in seconds

        Returns:
            Sandbox instance
        """
        if session_id in self._sandboxes:
            logger.info(f"Reusing existing sandbox for session: {session_id}")
            return self._sandboxes[session_id]

        timeout = timeout or self._settings.sandbox_timeout

        if HAS_E2B:
            sandbox = await AsyncSandbox.create(
                timeout=timeout,
                api_key=self._settings.e2b_api_key,
            )
        else:
            sandbox = MockSandbox()

        self._sandboxes[session_id] = sandbox
        logger.info(f"Created new sandbox for session: {session_id}")
        return sandbox

    async def get_sandbox(self, session_id: str) -> Any | None:
        """Get an existing sandbox for a session.

        Args:
            session_id: Session identifier

        Returns:
            Sandbox instance or None
        """
        return self._sandboxes.get(session_id)

    async def execute_code(self, session_id: str, code: str) -> Any:
        """Execute code in a session's sandbox.

        Args:
            session_id: Session identifier
            code: Python code to execute

        Returns:
            Execution result
        """
        sandbox = await self.get_sandbox(session_id)
        if not sandbox:
            raise ValueError(f"No sandbox found for session: {session_id}")

        return await sandbox.run_code(code)

    async def write_file(self, session_id: str, filepath: str, content: str) -> None:
        """Write a file in the sandbox.

        Args:
            session_id: Session identifier
            filepath: Path to file
            content: File content
        """
        sandbox = await self.get_sandbox(session_id)
        if not sandbox:
            raise ValueError(f"No sandbox found for session: {session_id}")

        await sandbox.files.write(filepath, content)

    async def read_file(self, session_id: str, filepath: str) -> str:
        """Read a file from the sandbox.

        Args:
            session_id: Session identifier
            filepath: Path to file

        Returns:
            File content
        """
        sandbox = await self.get_sandbox(session_id)
        if not sandbox:
            raise ValueError(f"No sandbox found for session: {session_id}")

        return await sandbox.files.read(filepath)

    async def list_files(self, session_id: str, directory: str = "/") -> list:
        """List files in a sandbox directory.

        Args:
            session_id: Session identifier
            directory: Directory path

        Returns:
            List of files
        """
        sandbox = await self.get_sandbox(session_id)
        if not sandbox:
            raise ValueError(f"No sandbox found for session: {session_id}")

        return await sandbox.files.list(directory)

    async def destroy_sandbox(self, session_id: str) -> bool:
        """Destroy a sandbox.

        Args:
            session_id: Session identifier

        Returns:
            True if destroyed, False if not found
        """
        sandbox = self._sandboxes.pop(session_id, None)
        if sandbox:
            await sandbox.close()
            logger.info(f"Destroyed sandbox for session: {session_id}")
            return True
        return False

    async def destroy_all(self) -> None:
        """Destroy all sandboxes."""
        for session_id in list(self._sandboxes.keys()):
            await self.destroy_sandbox(session_id)


# Global sandbox manager instance
_manager_instance: SandboxManager | None = None


def get_sandbox_manager() -> SandboxManager:
    """Get or create the global sandbox manager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SandboxManager()
    return _manager_instance
