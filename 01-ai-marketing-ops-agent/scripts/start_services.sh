#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Starting local mock services with Docker Compose."
docker compose up -d --build

echo
echo "Mock services are starting:"
echo "  Marketing panel: http://localhost:8000"
echo "  Campaign REST API: http://localhost:8001"
echo "  Analytics GraphQL API: http://localhost:8002/graphql"
echo "  Project management API: http://localhost:8003"
echo
echo "Run the demo with:"
echo "  ./scripts/run_workflow.sh"
echo
echo "Follow service logs with:"
echo "  docker compose logs -f"
echo
echo "Stop services with:"
echo "  docker compose down"
