# Code Archaeology Tool - The Mentor 🤖

> An AI-powered assistant that helps developers navigate and understand codebases through intelligent analysis and guided learning paths.

[![CI/CD](https://github.com/yourusername/code-archaeology/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/code-archaeology/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

Code Archaeology Tool is your friendly AI mentor that helps you:

- **🎯 Find Entry Points**: Suggest the best files to start with for specific tasks
- **📚 Generate Learning Paths**: Create progressive learning journeys from simple to complex
- **🔍 Identify Core Modules**: Discover the most critical files in the codebase
- **📊 Complexity Mapping**: Visualize which parts are beginner-friendly vs. expert-level
- **💬 Interactive Chat**: Ask questions about the codebase in natural language

## 🏗️ Architecture

Built using modern AI and code analysis tools:

- **LangChain & LangGraph**: Agent orchestration and tool management
- **Groq/OpenAI/Anthropic**: LLM providers for intelligent responses
- **Radon**: Code complexity analysis
- **NetworkX**: Dependency graph analysis
- **Git**: Repository history analysis
- **Rich**: Beautiful terminal UI

## 📋 Prerequisites

- **Python 3.11+**
- **Git**
- **WSL2** (if on Windows)
- **Docker** (optional, for containerized usage)
- **API Key** from one of:
  - [Groq](https://console.groq.com/) (recommended - fast and free)
  - [OpenAI](https://platform.openai.com/)
  - [Anthropic](https://www.anthropic.com/)

## 🚀 Quick Start

### Option 1: Local Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/code-archaeology.git
cd code-archaeology
```

#### 2. Create a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows (WSL): source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

#### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
# For Groq (recommended)
GROQ_API_KEY=gsk_your-groq-key-here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile

# For OpenAI
# OPENAI_API_KEY=sk-your-openai-key-here
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4-turbo-preview

# For Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-opus-20240229
```

#### 5. Run Code Archaeology Tool

```bash
# Interactive chat mode
code-archaeology chat --repo-path /path/to/your/project

# Quick analysis (no LLM required for basic stats)
code-archaeology analyze --repo-path /path/to/your/project

# Show configuration
code-archaeology config

# Show version
code-archaeology version
```

### Option 2: Docker

#### 1. Build the image

```bash
docker build -t code-archaeology .
```

#### 2. Run with Docker Compose

```bash
# Edit .env with your API key
cp .env.example .env
nano .env

# Run interactive chat
docker-compose run code-archaeology chat --repo-path /workspace

# Run quick analysis
docker-compose run code-archaeology analyze --repo-path /workspace
```

#### 3. Or run directly with Docker

```bash
docker run -it \
  -e GROQ_API_KEY=your-key-here \
  -e LLM_PROVIDER=groq \
  -v $(pwd):/workspace \
  code-archaeology:latest chat --repo-path /workspace
```

## 📖 Usage Examples

### Interactive Chat Mode

```bash
$ code-archaeology chat --repo-path ~/projects/my-app

Code Archaeology Tool - The Mentor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I'll help you navigate this codebase!

Repository: /home/user/projects/my-app
LLM: groq (llama-3.1-70b-versatile)

Try asking:
  - Where should I start to add a new feature?
  - Show me the core modules
  - Create a learning path for authentication
  - What's the complexity map?

Type 'quit' or 'exit' to end the session

You > Where should I start to add a payment processing feature?

Code Archaeology Tool > Based on my analysis of your codebase, here are the best entry points
for adding payment processing:

1. **src/payments/__init__.py**
   - File name contains 'payment'
   - Importance score: 45.2, Dependencies: 3, Dependents: 8
   - This is already the payment module - perfect starting point!

2. **src/services/transaction_service.py**
   - Contains symbol 'TransactionProcessor'
   - Importance score: 38.7, Dependencies: 5, Dependents: 12
   - Core service that handles transactions

3. **src/api/payment_endpoints.py**
   - File name contains 'payment'
   - Contains symbol 'create_payment'
   - This is where payment APIs are defined

I recommend starting with src/payments/__init__.py to understand the existing
payment structure, then moving to src/services/transaction_service.py to see
how transactions are processed.
```

### Quick Analysis

```bash
$ code-archaeology analyze --repo-path ~/projects/my-app

Quick Codebase Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: /home/user/projects/my-app

Core Modules Analysis
═════════════════════

These are the most important modules to understand:

1. **src/core/database.py**
   - Core Score: 85.3/100
   - Used by 24 other modules
   - Importance: 92.1/100
   - Modified 156 times
   - 🌟 Critical: Essential for understanding the codebase

2. **src/models/user.py**
   - Core Score: 78.2/100
   - Used by 18 other modules
   - Importance: 81.5/100
   ...

Codebase Complexity Map
════════════════════════

Overview:
- Total Python files analyzed: 87
- Average complexity: 8.3
- High-risk files: 5

🟢 Simple Files (Great for beginners):

1. **src/utils/validators.py**
   - Complexity: 2.1
   - Maintainability: 85.3/100
   - Risk: low
   - 💡 Good for learning the codebase
...
```

### Example Queries

Here are some questions you can ask the Code Archaeology Tool:

**Finding Entry Points:**
- "Where should I start to fix the authentication bug?"
- "I need to add a new API endpoint, where do I begin?"
- "Show me the best files to start understanding the payment system"

**Learning Paths:**
- "Create a learning path for the user management system"
- "I want to understand how authentication works, what should I read in order?"
- "Generate a progressive learning path for the API layer"

**Core Modules:**
- "What are the most important files in this project?"
- "Show me the core modules"
- "Which files should I understand first?"

**Complexity Analysis:**
- "What's the complexity map?"
- "Show me which files are simple and which are complex"
- "What are the easiest files to start with?"

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/code_archaeology --cov-report=html

# Run specific test file
pytest tests/test_analyzers/test_ast_analyzer.py

# Run tests in Docker
docker-compose run test
```

## 🛠️ Development

### Project Structure

```
code-archaeology/
├── src/
│   └── code_archaeology/
│       ├── agents/           # Agent implementations
│       │   └── code_archaeology.py
│       ├── tools/            # LangChain tools
│       │   ├── entry_point_tool.py
│       │   ├── learning_path_tool.py
│       │   ├── core_modules_tool.py
│       │   └── complexity_map_tool.py
│       ├── analyzers/        # Code analysis modules
│       │   ├── ast_analyzer.py
│       │   ├── git_analyzer.py
│       │   ├── complexity_analyzer.py
│       │   └── dependency_analyzer.py
│       ├── orchestrator/     # LangGraph orchestration
│       │   └── config.py
│       └── cli/              # CLI interface
│           └── main.py
├── tests/                    # Test suite
├── docker/                   # Docker configurations
├── .github/workflows/        # CI/CD pipelines
├── pyproject.toml           # Project dependencies
├── Dockerfile               # Docker image definition
└── README.md                # This file
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## 🔧 Configuration

Configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `LLM_PROVIDER` | LLM provider (groq/openai/anthropic) | groq |
| `LLM_MODEL` | Model name | llama-3.1-70b-versatile |
| `TEMPERATURE` | LLM temperature (0.0-1.0) | 0.2 |
| `MAX_TOKENS` | Maximum tokens per response | 4000 |
| `MAX_ITERATIONS` | Max agent iterations | 5 |
| `REPO_PATH` | Default repository path | . |
| `LOG_LEVEL` | Logging level | INFO |

## 🎯 Use Cases

### For New Developers
- **Onboarding**: Quickly understand a new codebase
- **Learning**: Get guided learning paths for specific areas
- **Navigation**: Find where to make changes without guessing

### For Team Leads
- **Knowledge Sharing**: Help new team members get up to speed
- **Code Reviews**: Identify complex areas that need attention
- **Documentation**: Generate insights about codebase structure

### For Educators
- **Teaching**: Help students navigate open-source projects
- **Assignments**: Guide students to appropriate starting points
- **Learning**: Demonstrate real-world code organization

## 🐛 Troubleshooting

### Common Issues

**Issue: "GROQ_API_KEY not found"**
```bash
# Make sure you've created .env and added your API key
cp .env.example .env
nano .env  # Add your API key
```

**Issue: "Repository path does not exist"**
```bash
# Use absolute path or correct relative path
code-archaeology chat --repo-path /full/path/to/repo
```

**Issue: "Not a git repository"**
```bash
# Some features require git. Initialize git in your repo:
cd /path/to/repo
git init
git add .
git commit -m "Initial commit"
```

**Issue: Tests failing in WSL**
```bash
# Configure git in WSL
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Issue: Docker build fails**
```bash
# Clean Docker cache and rebuild
docker system prune -a
docker build --no-cache -t code-archaeology .
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on the foundation described in [CodebaseGPT architecture](./claude.md)
- Powered by LangChain and LangGraph
- Inspired by the need to help developers navigate complex codebases

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Happy Coding! 🚀**

Made with ❤️ for developers who want to understand code faster
