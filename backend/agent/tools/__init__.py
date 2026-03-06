"""Agent tools for sandbox operations."""
from typing import Any

from langchain_core.tools import tool


def get_sandbox_tools(sandbox_context: dict[str, Any]) -> list:
    """Get sandbox-related tools with the current sandbox context."""

    @tool
    async def execute_code(code: str) -> str:
        """Execute Python code in the sandbox.

        Args:
            code: Python code to execute

        Returns:
            Execution result as string
        """
        if "execute" not in sandbox_context:
            return "Error: No sandbox available for code execution"

        try:
            result = await sandbox_context["execute"](code)
            output = []
            if result.logs.stdout:
                output.append(f"Output:\n{result.logs.stdout}")
            if result.logs.stderr:
                output.append(f"Error:\n{result.logs.stderr}")
            if result.error:
                output.append(f"Execution Error: {result.error}")
            if result.results:
                for r in result.results:
                    output.append(f"Result: {r}")
            return "\n".join(output) if output else "Code executed successfully (no output)"
        except Exception as e:
            return f"Error executing code: {str(e)}"

    @tool
    async def write_file(filepath: str, content: str) -> str:
        """Write content to a file in the sandbox.

        Args:
            filepath: Path to the file
            content: Content to write

        Returns:
            Success or error message
        """
        if "write_file" not in sandbox_context:
            return "Error: No sandbox available for file operations"

        try:
            await sandbox_context["write_file"](filepath, content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @tool
    async def read_file(filepath: str) -> str:
        """Read content from a file in the sandbox.

        Args:
            filepath: Path to the file

        Returns:
            File content or error message
        """
        if "read_file" not in sandbox_context:
            return "Error: No sandbox available for file operations"

        try:
            content = await sandbox_context["read_file"](filepath)
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @tool
    async def list_files(directory: str = "/") -> str:
        """List files in a directory in the sandbox.

        Args:
            directory: Directory path to list

        Returns:
            List of files or error message
        """
        if "list_files" not in sandbox_context:
            return "Error: No sandbox available for file operations"

        try:
            files = await sandbox_context["list_files"](directory)
            return "\n".join(str(f) for f in files)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @tool
    async def install_package(package: str) -> str:
        """Install a Python package in the sandbox.

        Args:
            package: Package name to install

        Returns:
            Installation result
        """
        if "execute" not in sandbox_context:
            return "Error: No sandbox available for package installation"

        try:
            result = await sandbox_context["execute"](f"!pip install {package}")
            return f"Package installation output:\n{result.logs.stdout}"
        except Exception as e:
            return f"Error installing package: {str(e)}"

    return [execute_code, write_file, read_file, list_files, install_package]


__all__ = ["get_sandbox_tools"]
