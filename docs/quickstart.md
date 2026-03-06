# Deep-Coder Quick Start Guide

This guide will help you get Deep-Coder up and running quickly.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.12+** (for local development)
- **Docker** and **Docker Compose** (for containerized deployment)
- **API Keys**:
  - [ZhipuAI API Key](https://open.bigmodel.cn/) (required)
  - [E2B API Key](https://e2b.dev/) (for sandbox execution)

## Quick Start (Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/deep-coder.git
cd deep-coder
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# ZhipuAI API key (required)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# E2B API key for sandbox execution
E2B_API_KEY=your_e2b_api_key_here
```

### 3. Deploy

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Start all services
./deploy.sh start
```

### 4. Access the Application

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Local Development

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Backend

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

### 5. Run Frontend (in a new terminal)

```bash
uv run streamlit run frontend/app.py
```

## Deployment Commands

The `deploy.sh` script provides several commands:

| Command | Description |
|---------|-------------|
| `./deploy.sh start` | Start all services |
| `./deploy.sh stop` | Stop all services |
| `./deploy.sh restart` | Restart all services |
| `./deploy.sh logs` | View logs (add `backend` or `frontend` to filter) |
| `./deploy.sh build` | Rebuild Docker images |
| `./deploy.sh clean` | Remove containers, volumes, and images |
| `./deploy.sh status` | Show service status |

## Usage

1. Open the Streamlit interface at http://localhost:8501
2. Enter your coding task in natural language (e.g., "Write a Python function to calculate Fibonacci numbers")
3. The agent will:
   - Analyze your request
   - Generate the code
   - Execute it in the sandbox
   - Show results and fix any errors

## Example Prompts

- "Write a Python script that reads a CSV file and calculates statistics"
- "Create a function to validate email addresses using regex"
- "Build a simple REST API using Flask"
- "Parse JSON data and visualize it with matplotlib"

## Troubleshooting

### Backend not starting

- Check if port 8000 is already in use
- Verify your API keys are correctly set in `.env`
- Check logs: `./deploy.sh logs backend`

### Frontend not connecting

- Ensure backend is running and healthy
- Check `BACKEND_URL` in Streamlit settings
- Check logs: `./deploy.sh logs frontend`

### Sandbox errors

- Verify your E2B API key is valid
- Check E2B service status at https://status.e2b.dev/
- The system will fall back to a mock sandbox if E2B is unavailable

### API Key Issues

- Ensure keys are not quoted in `.env`
- Check for trailing spaces
- Verify keys have not expired

## Next Steps

- Read the [Technical Design](technical-design.md) for architecture details
- Customize agent prompts in `backend/agent/prompts.py`
- Add custom tools in `backend/agent/tools/`

## Getting Help

- Open an issue on GitHub
- Check the documentation in the `docs/` directory
