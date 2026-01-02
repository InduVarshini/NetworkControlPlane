#!/bin/bash
# Helper script to run NetworkControlPlane in Docker

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "NetworkControlPlane - Docker Runner"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if image exists, build if not
if ! docker images | grep -q "network-control-plane"; then
    echo "📦 Building Docker image (this may take a few minutes)..."
    cd "$PROJECT_ROOT"
    docker build -t network-control-plane:latest .
    echo "✓ Image built successfully"
    echo ""
fi

# Run the container
echo "🚀 Starting NetworkControlPlane container..."
echo ""
echo "You can now run commands like:"
echo "  sudo python3 -m network_control_plane.cli deploy examples/topology.yaml"
echo "  sudo python3 -m network_control_plane.cli ping h1 h2"
echo "  sudo python3 examples/example_workflow.py"
echo ""
echo "Type 'exit' to stop the container"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"
docker run -it --rm --privileged \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    network-control-plane:latest \
    /bin/bash

