#!/bin/bash

# Deep-Coder One-Click Deployment Script
# Usage: ./deploy.sh [command]
# Commands: start, stop, restart, logs, build, clean

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_msg "Error: .env file not found!" "$RED"
        print_msg "Please copy .env.example to .env and configure your API keys:" "$YELLOW"
        print_msg "  cp .env.example .env" "$BLUE"
        print_msg "  # Edit .env and add your API keys" "$BLUE"
        exit 1
    fi

    # Check for required API keys
    source .env
    if [ -z "$ZHIPUAI_API_KEY" ]; then
        print_msg "Warning: ZHIPUAI_API_KEY not found in .env" "$YELLOW"
        print_msg "Please set ZHIPUAI_API_KEY for LLM access" "$YELLOW"
    fi

    if [ -z "$E2B_API_KEY" ]; then
        print_msg "Warning: E2B_API_KEY not found in .env" "$YELLOW"
        print_msg "Sandbox features will be limited without E2B API key" "$YELLOW"
    fi
}

# Check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_msg "Error: Docker is not installed!" "$RED"
        print_msg "Please install Docker: https://docs.docker.com/get-docker/" "$YELLOW"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_msg "Error: Docker Compose is not installed!" "$RED"
        print_msg "Please install Docker Compose: https://docs.docker.com/compose/install/" "$YELLOW"
        exit 1
    fi
}

# Build images
build() {
    print_msg "Building Docker images..." "$BLUE"
    docker-compose build --no-cache
    print_msg "Build complete!" "$GREEN"
}

# Start services
start() {
    build
    print_msg "Starting Deep-Coder services..." "$BLUE"
    check_env
    docker-compose up -d
    print_msg "Services started!" "$GREEN"
    print_msg "" "$NC"
    print_msg "Access the application:" "$GREEN"
    print_msg "  Frontend:  http://localhost:8501" "$BLUE"
    print_msg "  Backend:   http://localhost:8000" "$BLUE"
    print_msg "  API Docs:  http://localhost:8000/docs" "$BLUE"
}

# Stop services
stop() {
    print_msg "Stopping Deep-Coder services..." "$BLUE"
    docker-compose down
    print_msg "Services stopped!" "$GREEN"
}

# Restart services
restart() {
    stop
    start
}

# View logs
logs() {
    docker-compose logs -f "$@"
}

# Clean up
clean() {
    print_msg "Cleaning up Docker resources..." "$BLUE"
    docker-compose down -v --rmi local
    print_msg "Cleanup complete!" "$GREEN"
}

# Show status
status() {
    print_msg "Deep-Coder Status:" "$BLUE"
    docker-compose ps
}

# Main
case "${1:-start}" in
    start)
        check_docker
        start
        ;;
    stop)
        check_docker
        stop
        ;;
    restart)
        check_docker
        restart
        ;;
    logs)
        logs "${@:2}"
        ;;
    build)
        check_docker
        build
        ;;
    clean)
        check_docker
        clean
        ;;
    status)
        status
        ;;
    *)
        print_msg "Usage: $0 {start|stop|restart|logs|build|clean|status}" "$YELLOW"
        print_msg "" "$NC"
        print_msg "Commands:" "$BLUE"
        print_msg "  start   - Start all services" "$NC"
        print_msg "  stop    - Stop all services" "$NC"
        print_msg "  restart - Restart all services" "$NC"
        print_msg "  logs    - View logs (optional: backend/frontend)" "$NC"
        print_msg "  build   - Build Docker images" "$NC"
        print_msg "  clean   - Remove containers, volumes, and images" "$NC"
        print_msg "  status  - Show service status" "$NC"
        exit 1
        ;;
esac
