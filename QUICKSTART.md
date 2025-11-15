# Code Archaeology Tool - Quick Start Guide

This guide will get you up and running with Code Archaeology Tool in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Git installed
- A Groq API key (get one free at https://console.groq.com/)
- WSL2 (if on Windows)

## Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/code-archaeology.git
cd code-archaeology

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On WSL/Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
nano .env  # or use your favorite editor
```

Add your Groq API key:
```
GROQ_API_KEY=gsk_your-key-here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
```

## Usage

### Option 1: Interactive Chat

```bash
# Analyze any repository
code-archaeology chat --repo-path /path/to/your/project
```

Example interaction:
```
You > Show me the core modules

Code Archaeology Tool > Core Modules Analysis
These are the most important modules to understand:

1. **src/core/database.py**
   - Core Score: 85.3/100
   - Used by 24 other modules
   ...
```

### Option 2: Quick Analysis

```bash
# Get instant analysis without LLM
code-archaeology analyze --repo-path /path/to/your/project
```

### Option 3: Docker

```bash
# Build image
docker build -t code-archaeology .

# Run with your repository
docker run -it \
  -e GROQ_API_KEY=your-key \
  -v /path/to/your/repo:/workspace \
  code-archaeology:latest chat --repo-path /workspace
```

## Example Questions

Try asking Code Archaeology Tool:

- "Where should I start to add a payment feature?"
- "Create a learning path for authentication"
- "Show me the complexity map"
- "What are the core modules?"
- "I need to fix a bug in user management, where do I begin?"

## Test with Sample Repository

We include a sample repository for testing:

```bash
code-archaeology analyze --repo-path examples/sample_repo
```

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Make sure you created .env file and added your API key

### Issue: "Repository path does not exist"
**Solution:** Use absolute path: `/home/user/projects/myapp` not `~/projects/myapp`

### Issue: Git-related errors
**Solution:**
```bash
cd /path/to/your/repo
git init
git add .
git commit -m "Initial commit"
```

## What's Next?

- Read the full [README.md](README.md) for advanced usage
- Check out [claude.md](claude.md) for architecture details
- Run tests: `pytest tests/`
- Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Support

- Issues: https://github.com/yourusername/code-archaeology/issues
- Docs: Check the README.md

---

Happy coding! 🚀
