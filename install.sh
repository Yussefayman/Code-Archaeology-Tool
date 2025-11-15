#!/bin/bash
# Installation script for Code Archaeology Tool
# Supports both pip and uv

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Code Archaeology Tool - Installation     ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo ""

# Check Python version
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}Error: Python 3.11+ is required but not found${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo -e "${GREEN}✓ Python 3.11+ found${NC}"

# Ask user which installer to use
echo ""
echo -e "${YELLOW}Choose installation method:${NC}"
echo "  1) pip (standard)"
echo "  2) uv (10-100x faster, recommended)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo -e "\n${BLUE}Installing with pip...${NC}"

        # Create virtual environment
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3.11 -m venv venv
        source venv/bin/activate

        # Install dependencies
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install --upgrade pip
        pip install -e ".[dev]"

        echo -e "\n${GREEN}✓ Installation complete!${NC}"
        echo -e "${BLUE}Activate the environment with:${NC}"
        echo -e "  source venv/bin/activate"
        ;;

    2)
        echo -e "\n${BLUE}Installing with uv...${NC}"

        # Check if uv is installed
        if ! command -v uv &> /dev/null; then
            echo -e "${YELLOW}Installing uv...${NC}"
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.cargo/bin:$PATH"
        else
            echo -e "${GREEN}✓ uv already installed${NC}"
        fi

        # Create virtual environment with uv
        echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
        uv venv
        source .venv/bin/activate

        # Install dependencies with uv
        echo -e "${YELLOW}Installing dependencies with uv (this will be fast!)...${NC}"
        uv pip install -e ".[dev]"

        echo -e "\n${GREEN}✓ Installation complete!${NC}"
        echo -e "${BLUE}Activate the environment with:${NC}"
        echo -e "  source .venv/bin/activate"
        ;;

    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Copy .env.example to .env and add your API key"
echo "  2. Run: code-archaeology --help"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
