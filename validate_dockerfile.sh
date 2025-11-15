#!/bin/bash
# Validate Dockerfile.uv syntax and structure

set -e

echo "🔍 Validating Dockerfile.uv..."

# Check if file exists
if [ ! -f "Dockerfile.uv" ]; then
    echo "❌ Dockerfile.uv not found!"
    exit 1
fi

# Check for common issues
echo "✅ File exists"

# Check FROM instruction
if grep -q "^FROM python:" Dockerfile.uv; then
    echo "✅ Valid FROM instruction found"
else
    echo "❌ No valid FROM instruction"
    exit 1
fi

# Check UV installation
if grep -q "pip install.*uv" Dockerfile.uv; then
    echo "✅ UV installation via pip found"
else
    echo "❌ UV installation not found"
    exit 1
fi

# Check for venv usage (should NOT be present)
if grep -q "uv venv" Dockerfile.uv; then
    echo "❌ Found 'uv venv' - virtual environments should not be used in Docker!"
    exit 1
else
    echo "✅ No virtual environment usage (correct!)"
fi

# Check for --system flag
if grep -q "uv pip install --system" Dockerfile.uv; then
    echo "✅ Using --system flag (correct!)"
else
    echo "❌ --system flag not found"
    exit 1
fi

# Check WORKDIR
if grep -q "^WORKDIR" Dockerfile.uv; then
    echo "✅ WORKDIR set"
else
    echo "⚠️  No WORKDIR set"
fi

# Check for non-root user
if grep -q "useradd\|adduser" Dockerfile.uv; then
    echo "✅ Non-root user configuration found"
else
    echo "⚠️  No non-root user configuration"
fi

echo ""
echo "✅ Dockerfile.uv validation passed!"
echo ""
echo "To build the image, run:"
echo "  docker build -f Dockerfile.uv -t code-archaeology:uv ."
