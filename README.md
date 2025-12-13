# BugSpotter Intelligence

RAG (Retrieval-Augmented Generation) service for intelligent bug analysis and deduplication.

[![Tests](https://github.com/apexbridge-tech/bugspotter-intelligence/workflows/Tests/badge.svg)](https://github.com/apexbridge-tech/bugspotter-intelligence/actions) [![Python](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🚀 Features

- **Multi-LLM Support**: Extensible provider system supporting Ollama (local), Claude, and OpenAI
- **Registry Pattern**: Easy plugin architecture for adding new LLM providers
- **Semantic Deduplication**: Uses [DedupKit](https://github.com/apexbridge-tech/dedupkit) with pgvector for finding similar bugs
- **RAG-Ready**: Context-aware prompt building for better AI responses
- **Async FastAPI**: High-performance async API (coming soon)
- **Docker-First**: PostgreSQL + pgvector + Ollama included
- **Full Test Coverage**: Unit and integration tests with testcontainers

## 📋 Prerequisites

- Python 3.12+
- Docker Desktop
- 8GB+ RAM (for local LLM)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/apexbridge-tech/bugspotter-intelligence.git
cd bugspotter-intelligence
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e ".[dev]"
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Start Services
```bash
docker-compose up -d
```

Wait for Ollama to pull the model (first time ~5 minutes):
```bash
docker logs -f bugspotter-ollama
```

## 🧪 Run Tests
```bash
# Unit tests only (fast)
pytest tests/ -v -m "not integration"

# All tests including integration (requires Docker)
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/bugspotter_intelligence --cov-report=term-missing
```

## 🏗️ Architecture
```
bugspotter-intelligence/
├── src/bugspotter_intelligence/
│   ├── config.py              # Pydantic settings
│   ├── llm/                   # LLM provider abstraction
│   │   ├── base.py            # Abstract LLMProvider
│   │   ├── ollama.py          # Ollama implementation
│   │   ├── factory.py         # Registry pattern
│   │   └── __init__.py        # Public API
│   └── models/                # Data models (TODO)
├── docker/                    # Docker init scripts
│   ├── postgres/
│   │   └── init-db.sql        # pgvector setup
│   └── ollama/
│       └── ollama-init.sh     # Auto model download
├── tests/                     # Test suite
│   ├── conftest.py            # Pytest fixtures
│   └── llm/                   # LLM tests
└── docker-compose.yml         # Infrastructure
```

## 🤖 LLM Provider System

### Using Providers
```python
from bugspotter_intelligence.config import Settings
from bugspotter_intelligence.llm import create_llm_provider

# Create provider based on .env configuration
settings = Settings()
provider = create_llm_provider(settings)

# Generate response
response = await provider.generate(
    prompt="What causes null pointer exceptions?",
    context=[
        "Bug #1: App crashes on login with null pointer",
        "Bug #2: NullPointerException in auth module"
    ],
    temperature=0.7,
    max_tokens=200
)

print(response)
```

### Adding New Providers
```python
from bugspotter_intelligence.llm import register_provider, LLMProvider

@register_provider("my_llm")
class MyLLMProvider(LLMProvider):
    async def generate(self, prompt, context=None, **kwargs):
        # Your implementation
        return "AI response"
```

No changes to factory.py needed!

### Available Providers

- ✅ **Ollama** (local, free)
- 🚧 **Claude** (Anthropic, coming soon)
- 🚧 **OpenAI** (GPT-4, coming soon)

## 🔧 Configuration

Environment variables in `.env`:
```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5434
DATABASE_NAME=bugspotter_intelligence
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# LLM Provider (ollama, claude, openai)
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Claude Configuration (optional)
ANTHROPIC_API_KEY=your-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514

# App Settings
DEBUG=true
LOG_LEVEL=INFO
```

## 🐳 Docker Services

- **PostgreSQL 16** with pgvector extension
- **Ollama** with llama3.1:8b model (auto-downloaded)

## 📊 Development Roadmap

- [x] LLM provider abstraction with registry pattern
- [x] Ollama provider implementation
- [x] Docker Compose setup with pgvector
- [x] Comprehensive test suite
- [ ] FastAPI REST API routes
- [ ] Claude and OpenAI providers
- [ ] DedupKit integration for bug similarity
- [ ] Bug analysis endpoints
- [ ] Web UI

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [DedupKit](https://github.com/apexbridge-tech/dedupkit) - Semantic deduplication library
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Anthropic](https://anthropic.com/) - Claude API

## 📧 Contact

Apex Bridge Technology - [info@bugspotter.io](mailto:info@bugspotter.io)
