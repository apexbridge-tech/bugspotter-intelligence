# BugSpotter Intelligence

RAG (Retrieval-Augmented Generation) service for intelligent bug analysis and deduplication.

## Features

- 🤖 **Multi-LLM Support**: Ollama (local), Claude, OpenAI via extensible provider pattern
- 🔍 **Semantic Deduplication**: Using DedupKit library with pgvector
- 🚀 **Async FastAPI**: High-performance async API
- 🐳 **Docker Ready**: PostgreSQL + pgvector + Ollama included

## Quick Start

### Prerequisites
- Python 3.12+
- Docker Desktop
- 8GB+ RAM (for local LLM)

### Installation

\`\`\`bash
# Clone and setup
git clone <your-repo>
cd bugspotter-intelligence

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d
\`\`\`

### Run Tests

\`\`\`bash
pytest tests/ -v
\`\`\`

## Architecture

\`\`\`
bugspotter-intelligence/
├── src/bugspotter_intelligence/
│   ├── config.py          # Settings management
│   ├── llm/               # LLM provider abstraction
│   │   ├── base.py        # Abstract provider
│   │   ├── ollama.py      # Ollama implementation
│   │   └── factory.py     # Registry pattern
│   └── models/            # Pydantic models (TODO)
├── docker/                # Docker init scripts
├── tests/                 # Test suite
└── docker-compose.yml     # Infrastructure
\`\`\`

## LLM Providers

### Ollama (Local)
Default provider for development and self-hosted deployments.

\`\`\`python
# Automatically configured via .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
\`\`\`

### Adding New Providers

\`\`\`python
from bugspotter_intelligence.llm import register_provider, LLMProvider

@register_provider("my_provider")
class MyProvider(LLMProvider):
    async def generate(self, prompt, context=None, **kwargs):
        # Your implementation
        pass
\`\`\`

## License

MIT