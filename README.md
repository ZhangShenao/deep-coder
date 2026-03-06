# Deep-Coder

A lightweight AI coding agent built with LangGraph 1.0+ and ZhipuAI GLM-4-Flash that generates, executes, and debugs code in secure E2B sandboxes.

## Features

- **Natural Language to Code**: Describe your task, get working code
- **Secure Sandbox Execution**: Code runs in isolated E2B cloud sandboxes
- **Real-time Visualization**: Watch code generation and execution in real-time
- **Session Persistence**: Resume conversations with memory checkpointer
- **Iterative Debugging**: Agent automatically fixes and improves code

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   FastAPI +     │────▶│   E2B Sandbox   │
│   (Frontend)    │     │   LangGraph     │     │   (Execution)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Package Manager | uv |
| Agent Framework | LangGraph 1.0+ |
| LLM | ZhipuAI GLM-4-Flash |
| Sandbox | E2B Code Interpreter |
| Backend | FastAPI |
| Frontend | Streamlit |
| Checkpointer | InMemorySaver (MongoDB planned) |
| Deployment | Docker |

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- API Keys: ZhipuAI + E2B

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/deep-coder.git
cd deep-coder

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# One-click deployment
./deploy.sh start
```

### Option 2: Local Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run backend
uv run uvicorn backend.main:app --reload --port 8000

# Run frontend (in another terminal)
uv run streamlit run frontend/app.py
```

### Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
deep-coder/
├── backend/
│   ├── agent/          # LangGraph agent configuration & tools
│   ├── api/            # FastAPI routes & WebSocket
│   ├── sandbox/        # E2B sandbox manager
│   └── checkpoint/     # Session state persistence
├── frontend/
│   ├── app.py          # Streamlit main app
│   └── components/     # UI components
├── docker/             # Docker configuration
├── docs/               # Documentation
├── pyproject.toml      # Project dependencies
└── deploy.sh           # One-click deployment script
```

## Documentation

- [Technical Design](docs/technical-design.md) - Architecture and implementation details
- [Quick Start Guide](docs/quickstart.md) - Step-by-step setup instructions

## Configuration

Required environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `ZHIPUAI_API_KEY` | ZhipuAI API key (for GLM-4-Flash) |
| `E2B_API_KEY` | E2B sandbox API key |

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Type check
uv run mypy backend/
```

## License

MIT
