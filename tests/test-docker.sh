#!/bin/bash
# Quick test script to verify Docker setup

echo "Testing Docker setup..."
echo ""

# Check Docker
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon not running. Please start Docker Desktop."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if image exists
if docker images | grep -q "network-control-plane"; then
    echo "✓ Docker image exists"
else
    echo "⚠ Docker image not built yet. Run: docker build -t network-control-plane:latest ."
fi

echo ""
echo "Ready to run! Use one of these commands:"
echo "  ./docker-run.sh"
echo "  docker-compose up -d && docker-compose exec network-control-plane bash"
echo "  docker run -it --rm --privileged -v \$(pwd):/workspace -w /workspace network-control-plane:latest /bin/bash"
