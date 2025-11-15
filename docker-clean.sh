#!/bin/bash
# Clean up old Docker containers and images

echo "🧹 Cleaning up old Code Archaeology containers and images..."

# Stop and remove all code-archaeology containers
echo "Stopping containers..."
docker ps -a | grep code-archaeology | awk '{print $1}' | xargs -r docker stop 2>/dev/null || true

echo "Removing containers..."
docker ps -a | grep code-archaeology | awk '{print $1}' | xargs -r docker rm 2>/dev/null || true

# Remove images
echo "Removing images..."
docker images | grep code-archaeology | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "Now rebuild with:"
echo "  docker build --no-cache -f Dockerfile.uv -t code-archaeology:uv ."
