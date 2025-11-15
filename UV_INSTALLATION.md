# UV Installation Guide

This guide explains how to use [UV](https://github.com/astral-sh/uv) - an extremely fast Python package installer - with Code Archaeology Tool.

## Why UV?

UV is a blazing-fast Python package installer and resolver, written in Rust. It's **10-100x faster** than pip!

**Benefits:**
- ⚡ **Lightning fast** - Install dependencies in seconds, not minutes
- 🎯 **Drop-in replacement** - Works exactly like pip
- 🔒 **Reliable** - Better dependency resolution
- 💾 **Disk efficient** - Global cache reduces storage
- 🦀 **Modern** - Built with Rust for performance

## Installation Methods

### Method 1: Automated Install Script (Easiest)

```bash
git clone https://github.com/yourusername/code-archaeology.git
cd code-archaeology
./install.sh
```

Choose option **2** when prompted to use UV.

### Method 2: Manual Installation

#### Step 1: Install UV

**On Linux/macOS/WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Using pip:**
```bash
pip install uv
```

#### Step 2: Create Virtual Environment

```bash
# Create venv with uv (much faster than python -m venv)
uv venv

# Activate it
source .venv/bin/activate  # Linux/macOS/WSL
# or
.venv\Scripts\activate  # Windows
```

#### Step 3: Install Dependencies

```bash
# Install Code Archaeology Tool with uv
uv pip install -e ".[dev]"
```

That's it! ⚡

## Docker with UV

Build the UV-optimized Docker image:

```bash
docker build -f Dockerfile.uv -t code-archaeology:uv .
```

Run it:

```bash
docker run -it \
  -e GROQ_API_KEY=your-key-here \
  -v $(pwd):/workspace \
  code-archaeology:uv chat --repo-path /workspace
```

## Speed Comparison

Here's a real-world comparison on a typical machine:

| Method | Time to Install |
|--------|----------------|
| pip | ~45 seconds |
| uv | ~4 seconds |

**That's 11x faster!** 🚀

## CI/CD with UV

We provide a GitHub Actions workflow that uses UV:

```yaml
# .github/workflows/ci-uv.yml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
```

Check the full workflow in `.github/workflows/ci-uv.yml`.

## Common Commands

All pip commands work with uv:

```bash
# Install a package
uv pip install langchain

# Install from requirements
uv pip install -r requirements.txt

# Install in editable mode
uv pip install -e .

# Uninstall
uv pip uninstall package-name

# List installed packages
uv pip list

# Show package info
uv pip show package-name
```

## Troubleshooting

### UV command not found

Make sure UV is in your PATH:

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Permission errors

If you get permission errors during installation:

```bash
# Install uv for current user only
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Virtual environment activation issues

Make sure you're using the correct activation command:

```bash
# Linux/macOS/WSL
source .venv/bin/activate

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

## Learn More

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Benchmark](https://github.com/astral-sh/uv#benchmarks)
- [Astral Blog](https://astral.sh/blog)

---

**Ready to experience blazing-fast installations?** Try UV today! ⚡
