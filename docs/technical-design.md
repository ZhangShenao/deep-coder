# Deep-Coder 技术方案设计文档

## 1. 项目概述

### 1.1 项目背景
Deep-Coder 是一款基于 LangGraph 1.0+ 框架开发的智能编程助手，类似于 OpenCode。它能够根据用户需求自动生成代码，并在安全的沙箱环境中运行和调试，帮助开发者快速实现想法。

### 1.2 核心功能
- 自然语言描述需求，自动生成代码
- 代码在隔离沙箱中安全执行
- 实时展示执行过程和结果
- 支持代码迭代优化和调试
- 会话状态持久化保存

### 1.3 技术约束
- 后端：Python 3.12 + uv 依赖管理
- Agent 框架：LangGraph 1.0+
- LLM：智谱AI GLM-4-Flash
- 沙箱方案：E2B
- 前端：Streamlit
- 部署：Docker 容器化
- Checkpointer：InMemorySaver（初期），后续迁移至 MongoDB

---

## 2. 架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Deep-Coder System                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Frontend Layer                                │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Streamlit Web UI                             │  │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │  │   │
│  │  │  │  Chat Panel │  │ Code Viewer │  │  Execution Results  │    │  │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────┘    │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼ HTTP/WebSocket                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          Backend Layer                                │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                      FastAPI Server                             │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │  │   │
│  │  │  │  REST API    │  │  WebSocket   │  │   Session Manager    │ │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                    │                                  │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Agent Core (LangGraph 1.0+)                   │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │  │   │
│  │  │  │create_react  │  │   Sandbox    │  │    InMemorySaver     │ │  │   │
│  │  │  │   _agent     │  │    Tools     │  │    Checkpointer      │ │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────────┘ │  │   │
│  │  │                          │                                     │  │   │
│  │  │  ┌──────────────────────────────────────────────────────────┐ │  │   │
│  │  │  │                    ZhipuAI GLM-5-Flash                    │ │  │   │
│  │  │  └──────────────────────────────────────────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                    │                                  │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Checkpointer (InMemorySaver)                  │  │   │
│  │  │              [Future: MongoDB Checkpointer]                      │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Sandbox Layer (E2B)                           │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                     E2B Sandbox Manager                         │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │  │   │
│  │  │  │   Sandbox    │  │   Code       │  │    File System       │ │  │   │
│  │  │  │   Lifecycle  │  │   Executor   │  │    Operations        │ │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 架构分层说明

| 层级 | 组件 | 职责 |
|------|------|------|
| **Frontend Layer** | Streamlit UI | 用户交互、代码展示、执行结果可视化 |
| **Backend Layer** | FastAPI + LangGraph | API 服务、Agent 编排、会话管理 |
| **Sandbox Layer** | E2B | 代码安全执行、环境隔离、文件管理 |

---

## 3. 核心模块划分

### 3.1 模块结构图

```
deep-coder/
├── backend/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py              # LangGraph Agent 核心配置
│   │   ├── prompts.py           # System prompts 定义
│   │   └── tools/
│   │       ├── __init__.py
│   │       └── sandbox_tools.py # E2B 沙箱工具
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # 聊天 API
│   │   │   ├── sandbox.py       # 沙箱管理 API
│   │   │   └── session.py       # 会话管理 API
│   │   └── websocket.py         # WebSocket 处理
│   ├── sandbox/
│   │   ├── __init__.py
│   │   └── manager.py           # E2B 沙箱管理器
│   ├── checkpoint/
│   │   ├── __init__.py
│   │   └── memory_checkpoint.py # InMemorySaver Checkpointer
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py           # 请求模型
│   │   └── response.py          # 响应模型
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # 配置管理
│   └── main.py                  # 后端入口
├── frontend/
│   ├── app.py                   # Streamlit 主应用
│   └── utils/
│       ├── api_client.py        # API 客户端
│       └── session.py           # 会话工具
├── Dockerfile                   # 后端 Dockerfile
├── Dockerfile.frontend          # 前端 Dockerfile
├── docker-compose.yml           # Docker Compose 配置
├── pyproject.toml               # uv 项目配置
├── uv.lock                      # uv 锁文件
└── .env.example                 # 环境变量示例
```

### 3.2 核心模块详细设计

#### 3.2.1 Agent Core 模块

**文件**: `backend/agent/core.py`

```python
"""
LangGraph 1.0+ Agent 核心配置和初始化
"""
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from backend.agent.prompts import CODING_AGENT_SYSTEM_PROMPT
from backend.agent.tools import get_sandbox_tools
from backend.config import get_settings

class CodingAgent:
    def __init__(self, model_name: str = "glm-4-flash"):
        settings = get_settings()
        self.model = ChatZhipuAI(
            model=model_name,
            temperature=settings.llm_temperature,
            api_key=settings.zhipuai_api_key,
        )
        self.checkpointer = InMemorySaver()
        self._sandbox_tools = {}
        self._agent = None

    def set_sandbox_tools(self, sandbox_tools: dict):
        self._sandbox_tools = sandbox_tools

    def _create_agent(self):
        tools = get_sandbox_tools(self._sandbox_tools)
        return create_react_agent(
            model=self.model,
            tools=tools,
            state_modifier=CODING_AGENT_SYSTEM_PROMPT,
        )

    @property
    def agent(self):
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def invoke(self, message: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        return self.agent.invoke(
            {"messages": [HumanMessage(content=message)]},
            config,
        )
```

#### 3.2.2 Sandbox Manager 模块

**文件**: `backend/sandbox/manager.py`

```python
"""
E2B 沙箱管理器
"""
from typing import Optional
from e2b_code_interpreter import AsyncSandbox

class SandboxManager:
    def __init__(self):
        self._sandboxes: dict[str, AsyncSandbox] = {}

    async def create_sandbox(self, session_id: str, timeout: int = 300) -> AsyncSandbox:
        """创建新的沙箱实例"""
        sandbox = await AsyncSandbox.create(timeout=timeout)
        self._sandboxes[session_id] = sandbox
        return sandbox

    async def get_sandbox(self, session_id: str) -> Optional[AsyncSandbox]:
        """获取已存在的沙箱"""
        return self._sandboxes.get(session_id)

    async def execute_code(self, session_id: str, code: str):
        """在沙箱中执行代码"""
        sandbox = await self.get_sandbox(session_id)
        if not sandbox:
            raise ValueError(f"No sandbox found for session: {session_id}")
        return await sandbox.run_code(code)

    async def destroy_sandbox(self, session_id: str):
        """销毁沙箱"""
        sandbox = self._sandboxes.pop(session_id, None)
        if sandbox:
            await sandbox.close()
```

---

## 4. 技术栈选型

### 4.1 技术栈总览

| 类别 | 技术选型 | 版本要求 | 选型理由 |
|------|----------|----------|----------|
| **后端语言** | Python | 3.12+ | 与 LangChain/LangGraph 生态兼容，开发效率高 |
| **包管理** | uv | latest | 比 pip 快 10-100 倍，依赖解析更可靠 |
| **Agent 框架** | LangGraph | 1.0+ | LangChain 官方推荐，支持 React Agent、Checkpointer |
| **LLM 模型** | ZhipuAI GLM-4-Flash | - | 国产大模型，代码生成能力强，性价比高 |
| **Checkpointer** | InMemorySaver | - | 初期简单实现，快速迭代 |
| **Checkpointer (Future)** | MongoDB | 5.0+ | 持久化存储，支持分布式部署 |
| **沙箱方案** | E2B | latest | 开源、安全、快速启动，专为 AI 代码执行设计 |
| **Web 框架** | FastAPI | 0.115+ | 异步支持好，自动文档，性能优秀 |
| **前端框架** | Streamlit | 1.30+ | 快速开发，适合数据/代码展示场景 |
| **容器化** | Docker | 24.0+ | 标准化部署，环境一致性 |
| **编排工具** | Docker Compose | 2.20+ | 简单的多容器编排 |

### 4.2 依赖清单

```toml
# pyproject.toml
[project]
name = "deep-coder"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    # LangChain Core 1.0+
    "langchain>=0.3.0",
    "langchain-core>=0.3.0",
    "langchain-community>=0.3.0",
    # LangGraph 1.0+
    "langgraph>=0.3.0",
    "langgraph-checkpoint>=2.0.0",
    # ZhipuAI Integration
    "zhipuai>=2.0.0",
    # E2B Sandbox
    "e2b-code-interpreter>=1.0.0",
    # Web Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "websockets>=12.0",
    "httpx>=0.27.0",
    # Frontend
    "streamlit>=1.30.0",
    # Configuration
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]
```

---

## 5. 部署方案

### 5.1 环境变量配置

```bash
# .env.example

# ZhipuAI API Key (Required)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# E2B Sandbox API Key
E2B_API_KEY=your_e2b_api_key_here

# Application Settings
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# LLM Configuration
LLM_MODEL=glm-4-flash
LLM_TEMPERATURE=0.7

# Sandbox Configuration
SANDBOX_TIMEOUT=300

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 5.2 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}
      - E2B_API_KEY=${E2B_API_KEY}
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 6. 参考资料

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/)
- [LangChain Documentation](https://docs.langchain.com/)
- [ZhipuAI API Documentation](https://open.bigmodel.cn/dev/api)
- [E2B Documentation](https://e2b.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
