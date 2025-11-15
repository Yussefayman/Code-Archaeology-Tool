# Interactive Chat with Docker - Complete Guide

This guide shows you how to use Code Archaeology Tool's **interactive chat mode** with Docker.

## Quick Start

### 1. Build the Docker Image

First, build the Docker image using UV (fastest):

```bash
docker build -f Dockerfile.uv -t code-archaeology:uv .
```

Or use the standard Dockerfile (slower build):

```bash
docker build -t code-archaeology .
```

### 2. Set Your API Key

You need an LLM provider API key. Groq is recommended (free tier available):

```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

**Get a free Groq API key**: https://console.groq.com/keys

Alternative providers:
- OpenAI: `export OPENAI_API_KEY="your-key"`
- Anthropic: `export ANTHROPIC_API_KEY="your-key"`

## Running Interactive Chat

### Option 1: Analyze a Local Repository

Mount your local repository as a volume:

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -v /path/to/your/repo:/workspace \
  code-archaeology:uv chat --repo-path /workspace
```

**Example with current directory:**

```bash
cd ~/my-project

docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -v $(pwd):/workspace \
  code-archaeology:uv chat --repo-path /workspace
```

### Option 2: Analyze a GitHub Repository

No volume mounting needed! Just pass the GitHub URL:

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  code-archaeology:uv chat --repo-path https://github.com/django/django
```

**For private repositories**, add your GitHub token:

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -e GITHUB_TOKEN="your-github-token" \
  code-archaeology:uv chat --repo-path https://github.com/user/private-repo
```

## Understanding the Docker Flags

| Flag | Purpose | Required |
|------|---------|----------|
| `-i` | Interactive (keeps STDIN open) | ✅ Yes |
| `-t` | Allocates a pseudo-TTY (terminal) | ✅ Yes |
| `-e` | Sets environment variables | ✅ Yes (for API keys) |
| `-v` | Mounts volumes | Only for local repos |

**Important**: Always use `-it` together for interactive chat!

## Interactive Chat Commands

Once inside the chat, you can ask questions like:

```
You: Where should I start to add authentication?
Code Archaeology Tool: Based on the codebase structure...

You: Show me the core modules
Code Archaeology Tool: Here are the most important modules...

You: Create a learning path for the API
Code Archaeology Tool: Here's a progressive learning path...

You: What's the complexity map?
Code Archaeology Tool: Here's the complexity breakdown...
```

**Exit commands:**
- Type `quit`, `exit`, or `bye` to end the session
- Press `Ctrl+C` to interrupt

## Complete Examples

### Example 1: Chat with Django Repository

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  code-archaeology:uv chat --repo-path https://github.com/django/django
```

**Sample interaction:**
```
Code Archaeology Tool - Your AI mentor for navigating codebases
✓ Ready to chat!

Try asking:
  - Where should I start to add a new feature?
  - Show me the core modules
  - Create a learning path for authentication
  - What's the complexity map?

Type 'quit' or 'exit' to end the session

You: Where should I start to understand Django's ORM?

Code Archaeology Tool (thinking...)

# Entry Points for "understand Django's ORM"

Based on the codebase analysis, here are the best entry points...
[continues with detailed response]

You: quit

Goodbye! Happy coding! 👋
Cleaning up temporary files...
```

### Example 2: Chat with Your Local Project

```bash
cd ~/projects/my-web-app

docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -v $(pwd):/workspace \
  code-archaeology:uv chat --repo-path /workspace
```

### Example 3: Using OpenAI Instead of Groq

```bash
docker run -it \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -v $(pwd):/workspace \
  code-archaeology:uv chat \
    --repo-path /workspace \
    --llm-provider openai
```

### Example 4: Chat with Private GitHub Repo

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -e GITHUB_TOKEN="ghp_xxxxxxxxxxxx" \
  code-archaeology:uv chat --repo-path https://github.com/mycompany/private-api
```

## Using Docker Compose for Easy Setup

Create a `.env` file:

```bash
GROQ_API_KEY=your-groq-api-key
REPO_PATH=/path/to/your/repo
```

Run with docker-compose:

```bash
docker-compose run code-archaeology chat --repo-path /workspace
```

The compose file handles all the volume mounting and environment variables!

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Solution**: Make sure Docker is running:
```bash
# Linux/macOS
sudo systemctl start docker

# Or start Docker Desktop on macOS/Windows
```

### Issue: Chat doesn't accept input

**Problem**: Missing `-it` flags

**Solution**: Always use `-it` together:
```bash
docker run -it ...  # ✅ Correct
docker run -i ...   # ❌ No TTY
docker run -t ...   # ❌ No input
docker run ...      # ❌ Not interactive
```

### Issue: "API key not found"

**Solution**: Make sure to pass the API key as an environment variable:
```bash
# ❌ Wrong - key not passed to container
export GROQ_API_KEY="xxx"
docker run -it code-archaeology:uv chat ...

# ✅ Correct - key passed with -e flag
export GROQ_API_KEY="xxx"
docker run -it -e GROQ_API_KEY="$GROQ_API_KEY" code-archaeology:uv chat ...
```

### Issue: "Permission denied" accessing local repository

**Solution**: Check your volume mount path:
```bash
# Use absolute paths
docker run -it -v /home/user/project:/workspace ...  # ✅ Good

# Or use $(pwd) for current directory
docker run -it -v $(pwd):/workspace ...  # ✅ Good

# Don't use relative paths
docker run -it -v ./project:/workspace ...  # ❌ May not work
```

### Issue: Chat is slow to respond

**Cause**: LLM provider latency

**Solutions**:
- Use Groq (fastest, optimized for speed)
- Analyze smaller repositories
- The tool caches repository analysis locally

### Issue: "Repository not found" for GitHub URL

**Causes**:
1. Private repository without token
2. Invalid URL format
3. Network connectivity

**Solutions**:
```bash
# For private repos, add GITHUB_TOKEN
docker run -it \
  -e GROQ_API_KEY="xxx" \
  -e GITHUB_TOKEN="ghp_xxx" \
  code-archaeology:uv chat --repo-path https://github.com/user/private-repo

# Verify URL format (all these work):
https://github.com/django/django
git@github.com:django/django.git
github.com/django/django
```

## Tips for Better Chat Experience

### 1. Be Specific in Questions

**Good questions:**
- "Where should I start to add user authentication?"
- "Show me the most complex files in the API module"
- "Create a learning path for understanding the database layer"

**Less effective:**
- "Tell me about this code"
- "What does this do?"

### 2. Use the Suggested Commands

The tool provides helpful suggestions when you start:
```
Try asking:
  - Where should I start to add a new feature?
  - Show me the core modules
  - Create a learning path for authentication
  - What's the complexity map?
```

### 3. Leverage Chat History

The tool remembers your last 5 exchanges, so you can build on previous questions:

```
You: Show me the core modules
...
You: Which of these handles authentication?
...
You: Create a learning path starting from that module
```

### 4. Analyze Before Chatting

For faster chat responses, run a quick analysis first:

```bash
# First, analyze
docker run -e GROQ_API_KEY="xxx" \
  code-archaeology:uv analyze --repo-path https://github.com/django/django

# Then chat (analysis is cached)
docker run -it -e GROQ_API_KEY="xxx" \
  code-archaeology:uv chat --repo-path https://github.com/django/django
```

## Advanced: Persistent Analysis Cache

To avoid re-analyzing the same repository, mount a cache volume:

```bash
docker run -it \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -v $(pwd):/workspace \
  -v ~/.code-archaeology-cache:/root/.cache \
  code-archaeology:uv chat --repo-path /workspace
```

This speeds up subsequent chats with the same repository!

## What's Happening Behind the Scenes?

When you run chat mode with Docker:

1. **Container starts** with the specified image
2. **Environment variables** are loaded (API keys)
3. **Repository is accessed**:
   - Local: Via volume mount at `/workspace`
   - GitHub: Cloned to temporary directory automatically
4. **Analysis runs**: AST parsing, git history, complexity, dependencies
5. **Agent initializes**: Loads LLM and specialized tools
6. **Interactive loop starts**: Accepts your questions
7. **On exit**: Temporary files are cleaned up

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for basic usage
- Read [DOCKER.md](DOCKER.md) for advanced Docker configuration
- Read [README.md](README.md) for full documentation
- Try the [analyze command](README.md#analyze-command) for quick insights

## Getting Help

**Need an API key?**
- Groq (recommended): https://console.groq.com/keys
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

**Issues?**
- Check [TROUBLESHOOTING.md](README.md#troubleshooting)
- Open an issue on GitHub
- Make sure Docker is running and you have network access

---

**Happy code archaeology! 🏛️🔍**
