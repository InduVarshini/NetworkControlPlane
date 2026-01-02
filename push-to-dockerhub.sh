#!/bin/bash
# Script to build and push NetworkControlPlane Docker image to Docker Hub
#
# Usage:
#   ./push-to-dockerhub.sh [DOCKERHUB_USERNAME] [TAG]
#
# Example:
#   ./push-to-dockerhub.sh myusername latest
#   ./push-to-dockerhub.sh myusername v1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get Docker Hub username from argument or prompt
if [ -z "$1" ]; then
    echo -e "${YELLOW}Docker Hub username not provided.${NC}"
    read -p "Enter your Docker Hub username: " DOCKERHUB_USERNAME
else
    DOCKERHUB_USERNAME=$1
fi

# Get tag from argument or use default
TAG=${2:-latest}
IMAGE_NAME="network-control-plane"

# Full image name
FULL_IMAGE_NAME="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

echo -e "${GREEN}Building and pushing NetworkControlPlane to Docker Hub${NC}"
echo -e "Image: ${FULL_IMAGE_NAME}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}Not logged in to Docker Hub.${NC}"
    echo "Please login: docker login"
    read -p "Press Enter to continue after logging in, or Ctrl+C to cancel..."
fi

# Build the image
echo -e "${GREEN}Building Docker image...${NC}"
docker build -t "${FULL_IMAGE_NAME}" -t "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest" .

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

# Push the image
echo -e "${GREEN}Pushing to Docker Hub...${NC}"
docker push "${FULL_IMAGE_NAME}"

if [ "$TAG" != "latest" ]; then
    echo -e "${GREEN}Also pushing latest tag...${NC}"
    docker push "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Successfully pushed to Docker Hub!${NC}"
    echo -e "Image: ${FULL_IMAGE_NAME}"
    echo ""
    echo "To pull and run:"
    echo "  docker pull ${FULL_IMAGE_NAME}"
    echo "  docker run -it --rm --privileged -p 5001:5001 ${FULL_IMAGE_NAME}"
else
    echo -e "${RED}Push failed!${NC}"
    exit 1
fi

