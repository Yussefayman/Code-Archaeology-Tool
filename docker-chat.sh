#!/bin/bash
# Simple script to run Code Archaeology Tool chat with Docker

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Code Archaeology Tool - Docker Chat${NC}"
echo ""

# Check if API key is set
if [ -z "$GROQ_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: No API key found!${NC}"
    echo ""
    echo "Please set one of these environment variables:"
    echo "  export GROQ_API_KEY='your-key'        (Recommended - fastest)"
    echo "  export OPENAI_API_KEY='your-key'"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo ""
    echo "Get a free Groq API key: https://console.groq.com/keys"
    exit 1
fi

# Determine which API key to use
API_KEY_FLAG=""
if [ ! -z "$GROQ_API_KEY" ]; then
    API_KEY_FLAG="-e GROQ_API_KEY=$GROQ_API_KEY"
    echo -e "${GREEN}✓ Using Groq API${NC}"
elif [ ! -z "$OPENAI_API_KEY" ]; then
    API_KEY_FLAG="-e OPENAI_API_KEY=$OPENAI_API_KEY"
    echo -e "${GREEN}✓ Using OpenAI API${NC}"
elif [ ! -z "$ANTHROPIC_API_KEY" ]; then
    API_KEY_FLAG="-e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
    echo -e "${GREEN}✓ Using Anthropic API${NC}"
fi

# Add GitHub token if available
GITHUB_TOKEN_FLAG=""
if [ ! -z "$GITHUB_TOKEN" ]; then
    GITHUB_TOKEN_FLAG="-e GITHUB_TOKEN=$GITHUB_TOKEN"
    echo -e "${GREEN}✓ GitHub token found (can access private repos)${NC}"
fi

# Check if Docker image exists
if ! docker image inspect code-archaeology:uv >/dev/null 2>&1; then
    echo -e "${YELLOW}Docker image not found. Building...${NC}"
    docker build -f Dockerfile.uv -t code-archaeology:uv .
    echo -e "${GREEN}✓ Build complete!${NC}"
fi

echo ""

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <repo-path-or-github-url>"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/local/repo"
    echo "  $0 \$(pwd)                              # Current directory"
    echo "  $0 https://github.com/django/django"
    echo "  $0 https://github.com/fastapi/fastapi"
    echo ""
    exit 1
fi

REPO_INPUT="$1"

# Check if input is a GitHub URL
if [[ "$REPO_INPUT" =~ ^https?://github\.com ]] || [[ "$REPO_INPUT" =~ ^github\.com ]] || [[ "$REPO_INPUT" =~ ^git@github\.com ]]; then
    # GitHub URL - no volume mount needed
    echo -e "${GREEN}Analyzing GitHub repository: $REPO_INPUT${NC}"
    echo ""

    docker run -it \
        $API_KEY_FLAG \
        $GITHUB_TOKEN_FLAG \
        code-archaeology:uv chat --repo-path "$REPO_INPUT"
else
    # Local path - need volume mount
    # Convert to absolute path
    ABS_PATH=$(cd "$REPO_INPUT" && pwd)

    echo -e "${GREEN}Analyzing local repository: $ABS_PATH${NC}"
    echo ""

    docker run -it \
        $API_KEY_FLAG \
        $GITHUB_TOKEN_FLAG \
        -v "$ABS_PATH:/workspace" \
        code-archaeology:uv chat --repo-path /workspace
fi
