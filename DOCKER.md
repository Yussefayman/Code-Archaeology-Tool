# Docker Guide for Code Archaeology Tool

This guide explains how to use Docker with Code Archaeology Tool.

## Why No Virtual Environments in Docker?

You might notice our Dockerfiles **don't use virtual environments** (venv). This is intentional and follows Docker best practices:

### Docker Already Provides Isolation

- **Docker containers are isolated** - They have their own filesystem, processes, and network
- **No dependency conflicts** - Each container has its own Python environment
- **Virtual envs are redundant** - They solve a problem Docker already solves
- **Simpler Dockerfiles** - Less complexity, faster builds
- **Smaller images** - No venv overhead

### When to Use Virtual Environments

| Environment | Use Venv? | Why |
|-------------|-----------|-----|
| **Local development** | ✅ Yes | Isolate from system Python |
| **Docker container** | ❌ No | Docker provides isolation |
| **CI/CD runners** | ✅ Yes | Multiple jobs share runners |
| **Production server** | ✅ Yes | Multiple apps on same server |

## Available Dockerfiles

### 1. Standard Dockerfile (pip)

Uses pip for package installation:

```bash
docker build -t code-archaeology .
```

**Features:**
- Multi-stage build for smaller images
- Uses pip for installation
- Production-ready

### 2. UV-Optimized Dockerfile (faster!)

Uses UV for ultra-fast installation:

```bash
docker build -f Dockerfile.uv -t code-archaeology:uv .
```

**Features:**
- Uses UV (10-100x faster than pip)
- Single-stage build (simpler)
- Direct system installation with `uv pip install --system`
- No virtual environment overhead

**Key difference in UV Dockerfile:**
```dockerfile
# ✅ Correct: Direct system installation
RUN uv pip install --system -e .

# ❌ Wrong: Unnecessary venv in Docker
# RUN uv venv && source venv/bin/activate && uv pip install -e .
```

## Usage Examples

### Basic Usage

```bash
# Build
docker build -f Dockerfile.uv -t code-archaeology:uv .

# Run with local repository
docker run -it \
  -e GROQ_API_KEY=your-key \
  -v $(pwd):/workspace \
  code-archaeology:uv analyze --repo-path /workspace

# Run with GitHub URL
docker run -it \
  -e GROQ_API_KEY=your-key \
  code-archaeology:uv analyze --repo-path https://github.com/django/django
```

### With Docker Compose

```bash
# Edit .env with your API key
cp .env.example .env
nano .env

# Run
docker-compose run code-archaeology chat --repo-path /workspace
```

### Interactive Chat

```bash
docker run -it \
  -e GROQ_API_KEY=your-key \
  -v /path/to/repo:/workspace \
  code-archaeology:uv chat --repo-path /workspace
```

## Docker Compose

Our `docker-compose.yml` provides easy configuration:

```yaml
services:
  code-archaeology:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ${REPO_PATH:-.}:/workspace:ro
    command: chat --repo-path /workspace
```

**Usage:**
```bash
# Set up environment
export GROQ_API_KEY=your-key
export REPO_PATH=/path/to/repo

# Run
docker-compose run code-archaeology analyze --repo-path /workspace
```

## Best Practices

### 1. Don't Use Virtual Environments

```dockerfile
# ❌ Bad: Unnecessary in Docker
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -e .

# ✅ Good: Direct installation
RUN pip install -e .
```

### 2. Use Multi-Stage Builds (for pip)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
RUN pip install -e .

# Stage 2: Runtime (smaller image)
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

### 3. Use --system flag with UV

```dockerfile
# ✅ Correct: Tell UV to install system-wide
RUN uv pip install --system -e .

# ❌ Wrong: UV will complain without --system
RUN uv pip install -e .
```

### 4. Don't Run as Root

```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### 5. Set Python Environment Variables

```dockerfile
ENV PYTHONUNBUFFERED=1        # Don't buffer output
ENV PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files
```

## Troubleshooting

### Error: "This interpreter is externally managed"

**Problem:** UV tries to use venv by default

**Solution:** Use `--system` flag:
```dockerfile
RUN uv pip install --system -e .
```

### Error: "command not found: uv"

**Problem:** UV not in PATH

**Solution:** Add UV to PATH:
```dockerfile
ENV PATH="/root/.cargo/bin:$PATH"
```

### Large Image Size

**Problem:** Image is too large

**Solutions:**
1. Use multi-stage builds
2. Clean up apt cache: `rm -rf /var/lib/apt/lists/*`
3. Use `--no-cache-dir` with pip
4. Use `.dockerignore` to exclude unnecessary files

## Performance Comparison

| Dockerfile | Build Time | Image Size | Method |
|------------|------------|------------|--------|
| Standard (pip) | ~2-3 min | ~450 MB | Multi-stage |
| UV-optimized | ~30-45 sec | ~420 MB | Single-stage |

**UV is 4-6x faster!** 🚀

## Security Considerations

1. **Don't include secrets in image**
   ```bash
   # ✅ Good: Pass via environment
   docker run -e GROQ_API_KEY=xxx ...

   # ❌ Bad: Hardcode in Dockerfile
   ENV GROQ_API_KEY=xxx
   ```

2. **Use non-root user**
   - All our Dockerfiles create and use `appuser`

3. **Keep images updated**
   ```bash
   docker build --pull -t code-archaeology .
   ```

4. **Use specific base image tags**
   ```dockerfile
   # ✅ Good: Specific version
   FROM python:3.11-slim

   # ❌ Bad: Latest (unpredictable)
   FROM python:latest
   ```

## Conclusion

**Key Takeaway:** Virtual environments are for local development. In Docker, install packages directly to the system Python for simplicity and efficiency.

For more details, see:
- [Python official Docker guide](https://docs.python.org/3/using/unix.html#building-python)
- [Docker best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [UV documentation](https://github.com/astral-sh/uv)
