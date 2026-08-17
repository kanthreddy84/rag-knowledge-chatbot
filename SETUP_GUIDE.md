# Setup & Installation Guide

**Project:** HR Policy Knowledge Chatbot  
**Python Version:** 3.10 or higher  
**Last Updated:** 2026-08-14

---

## Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Environment File
```bash
# Create .env file
cat > .env << 'EOF'
# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Pinecone Vector Database
PINECONE_API_KEY=pcn-your-key-here
PINECONE_REGION=us-east-1

# Together AI (Llama Embeddings)
TOGETHER_API_KEY=your-key-here

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag_chatbot

# Optional: OpenAI (if using alternative embeddings)
OPENAI_API_KEY=sk-your-key-here
EOF
```

### Step 3: Test Installation
```bash
python -c "
import anthropic
import pinecone
import together
print('✅ All dependencies installed successfully!')
"
```

---

## Detailed Installation

### Prerequisites

**System Requirements:**
- Python 3.10+
- pip package manager
- Git (for version control)
- 2GB+ disk space
- Internet connection

**Check Python Version:**
```bash
python --version  # Should be 3.10.0 or higher
pip --version
```

### Installation Steps

**1. Clone/Setup Project**
```bash
cd "C:\AI Projects\RAG Knowledge Chatbot"
```

**2. Create Virtual Environment (Recommended)**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Upgrade pip**
```bash
pip install --upgrade pip
```

**4. Install Requirements**
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "anthropic|pinecone|together|openai|fastapi"
```

**5. Get API Keys**

**Anthropic Claude:**
- Go to: https://console.anthropic.com/
- Create account (free tier available)
- Generate API key
- Save to .env: `ANTHROPIC_API_KEY=sk-ant-...`

**Pinecone Vector DB:**
- Go to: https://www.pinecone.io/
- Create free account (free tier: $0/month)
- Create index "hr-policy-kb"
- Save API key to .env: `PINECONE_API_KEY=pcn-...`

**Together AI (Llama Embeddings):**
- Go to: https://www.together.ai/
- Create account (free tier available)
- Generate API key
- Save to .env: `TOGETHER_API_KEY=...`

**PostgreSQL (Optional for full deployment):**
- Install: https://www.postgresql.org/download/
- Or use managed service (AWS RDS, Azure Database)
- Create database: `rag_chatbot`
- Save connection to .env: `DATABASE_URL=postgresql://...`

**6. Create .env File**
```bash
# Copy template
cp .env.example .env  # if available

# Or create manually
echo "ANTHROPIC_API_KEY=your-key" >> .env
echo "PINECONE_API_KEY=your-key" >> .env
echo "TOGETHER_API_KEY=your-key" >> .env
```

---

## Dependency Overview

### Core Dependencies

| Package | Version | Purpose | Cost |
|---------|---------|---------|------|
| **anthropic** | 0.34.0 | Claude LLM API | $3-15 per 1M tokens |
| **together** | 1.2.0 | Llama embeddings | $0.10 per 1M tokens |
| **pinecone-client** | 5.1.0 | Vector database | $0/month (free tier) |

### Document Processing

| Package | Version | Purpose |
|---------|---------|---------|
| **pypdf** | 4.2.0 | PDF parsing |
| **python-docx** | 1.2.0 | DOCX parsing |
| **beautifulsoup4** | 4.12.3 | HTML parsing |

### Backend & API

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | 0.110.3 | REST API framework |
| **uvicorn** | 0.27.0 | ASGI server |
| **sqlalchemy** | 2.0.27 | ORM for database |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| **pydantic** | 2.6.4 | Data validation |
| **python-dotenv** | 1.0.1 | Environment variables |
| **tiktoken** | 0.7.0 | Token counting |

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: API key not found

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify format (no quotes around keys)
ANTHROPIC_API_KEY=sk-ant-xxxx  # ✅ Correct
ANTHROPIC_API_KEY="sk-ant-xxxx"  # ❌ Wrong

# Load environment
source .env  # Mac/Linux
set -a && source .env && set +a  # Bash
```

### Issue: Pinecone connection failed

**Solution:**
```bash
# Test Pinecone connection
python -c "
import pinecone
pinecone.init(api_key='YOUR_KEY', region='us-east-1')
pc = pinecone.Pinecone()
print('✅ Pinecone connected!')
"
```

### Issue: Claude API authentication failed

**Solution:**
```bash
# Test Anthropic connection
python -c "
from anthropic import Anthropic
client = Anthropic(api_key='YOUR_KEY')
print('✅ Anthropic connected!')
"
```

---

## Verification Checklist

### Run This to Verify Installation

```bash
python << 'EOF'
import sys
print(f"Python Version: {sys.version}")

# Test all imports
try:
    import anthropic
    print("✅ anthropic: OK")
except ImportError as e:
    print(f"❌ anthropic: FAILED - {e}")

try:
    import pinecone
    print("✅ pinecone: OK")
except ImportError as e:
    print(f"❌ pinecone: FAILED - {e}")

try:
    import together
    print("✅ together: OK")
except ImportError as e:
    print(f"❌ together: FAILED - {e}")

try:
    import fastapi
    print("✅ fastapi: OK")
except ImportError as e:
    print(f"❌ fastapi: FAILED - {e}")

try:
    from PyPDF2 import PdfReader
    print("✅ pypdf: OK")
except ImportError as e:
    print(f"❌ pypdf: FAILED - {e}")

try:
    from docx import Document
    print("✅ python-docx: OK")
except ImportError as e:
    print(f"❌ python-docx: FAILED - {e}")

try:
    from bs4 import BeautifulSoup
    print("✅ beautifulsoup4: OK")
except ImportError as e:
    print(f"❌ beautifulsoup4: FAILED - {e}")

print("\n✨ All dependencies verified!")
EOF
```

---

## Development Setup

### Code Quality Tools

**Install development dependencies:**
```bash
pip install black pylint flake8 mypy pytest pytest-asyncio
```

**Format code:**
```bash
black *.py
```

**Lint code:**
```bash
flake8 *.py
pylint *.py
```

**Type checking:**
```bash
mypy *.py
```

---

## Running the Code

### Test Document Chunking
```bash
python << 'EOF'
from document_chunking import HybridChunker

chunker = HybridChunker(strategy="hybrid")
chunks = chunker.chunk_document("sample_policy.pdf")
print(f"Created {len(chunks)} chunks")
for chunk in chunks[:3]:
    print(f"  - Chunk {chunk.chunk_number}: {chunk.section_path}")
EOF
```

### Test Embeddings
```bash
python << 'EOF'
from embedding_module_llama import LlamaEmbeddingAndVectorPipeline, EmbeddingConfig
import os

config = EmbeddingConfig(
    model="llama",
    embedding_model_name="meta-llama-3-8b-instruct",
    api_key=os.getenv("TOGETHER_API_KEY")
)

pipeline = LlamaEmbeddingAndVectorPipeline(config)
# Test with sample text
test_text = "What is the vacation policy?"
result = pipeline.embed_query(test_text)
print(f"✅ Embedding generated: {len(result)} dimensions")
EOF
```

### Test LLM Generation
```bash
python << 'EOF'
from llm_answer_generation import LLMConfig, RAGAnswerGenerator
import os

config = LLMConfig(
    model="claude",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

generator = RAGAnswerGenerator(config)
# Note: Requires retrieved_chunks from vector DB
print("✅ LLM Generator initialized")
EOF
```

---

## Next Steps

1. **Collect Documents** - Gather 15-30 HR policy documents
2. **Process Documents** - Run document_chunking.py on your policies
3. **Embed & Index** - Run embedding_module_llama.py
4. **Test Answers** - Run llm_answer_generation.py
5. **Deploy API** - Use FastAPI to expose REST endpoints

---

## Support

**Common Issues:**
- Missing API keys → Check .env file
- Module import errors → Reinstall requirements.txt
- Connection timeouts → Check internet & API status
- Memory issues → Increase system RAM or batch size

**Additional Resources:**
- See README.md for full project documentation
- Check individual module files for detailed comments

---

## Cost Summary

```
Monthly Cost (1,000 queries/month):
├─ Anthropic Claude:    $1.13 (for 75K output tokens)
├─ Together AI Llama:    $0.10 (for 200K tokens)
├─ Pinecone:             $0.00 (free tier)
└─ Total:                ~$1.23/month

Annual Cost: ~$15/year (extremely cost-effective!)
```

---

**Setup Complete!** Ready to start building your chatbot. 🎉

