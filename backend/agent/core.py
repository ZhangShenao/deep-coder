"""Coding Agent core using LangGraph 1.0+ and ZhipuAI GLM-4-Flash."""
from __future__ import annotations

import os
from typing import Any

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from backend.agent.prompts import CODING_AGENT_SYSTEM_PROMPT
from backend.agent.tools import get_sandbox_tools
from backend.config import get_settings


def _create_zhipuai_model(model_name: str, temperature: float):
    """Create ZhipuAI chat model instance."""
    settings = get_settings()
    api_key = settings.zhipuai_api_key or os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ZhipuAI API key is required. Set ZHIPUAI_API_KEY environment variable."
        )

    return ChatZhipuAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


class CodingAgent:
    """Coding agent powered by LangGraph and ZhipuAI GLM-4-Flash."""

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float | None = None,
    ):
        settings = get_settings()
        self.model_name = model_name or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.checkpointer = InMemorySaver()
        self._sandbox_tools: dict[str, Any] = {}
        self._agent = None

    def _create_model(self):
        """Initialize the ZhipuAI LLM model."""
        return _create_zhipuai_model(self.model_name, self.temperature)

    def set_sandbox_tools(self, sandbox_tools: dict[str, Any]) -> None:
        """Set sandbox tools for code execution."""
        self._sandbox_tools = sandbox_tools

    def _create_agent(self):
        """Create the react agent using LangGraph."""
        model = self._create_model()
        tools = get_sandbox_tools(self._sandbox_tools)

        # Create react agent with LangGraph 1.0+
        return create_react_agent(
            model=model,
            tools=tools,
            prompt=CODING_AGENT_SYSTEM_PROMPT,
        )

    @property
    def agent(self):
        """Lazy load the agent."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def invoke(self, message: str, thread_id: str) -> dict[str, Any]:
        """Invoke the agent with a message."""
        config = {"configurable": {"thread_id": thread_id}}

        return self.agent.invoke(
            {"messages": [HumanMessage(content=message)]},
            config,
        )

    async def ainvoke(self, message: str, thread_id: str) -> dict[str, Any]:
        """Async invoke the agent with a message."""
        config = {"configurable": {"thread_id": thread_id}}

        return await self.agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config,
        )

    async def astream(self, message: str, thread_id: str):
        """Stream agent execution."""
        config = {"configurable": {"thread_id": thread_id}}

        async for event in self.agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config,
            stream_mode="values",
        ):
            yield event


# Global agent instance
_agent_instance: CodingAgent | None = None


def get_coding_agent() -> CodingAgent:
    """Get or create the global coding agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CodingAgent()
    return _agent_instance
