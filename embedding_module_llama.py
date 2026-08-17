"""
Embedding and Vector Storage Module for RAG Knowledge Chatbot - LLAMA API VERSION

This module handles:
1. Document chunk embedding using Llama API (Meta's open-source LLM)
2. Vector storage in Pinecone
3. Semantic search and retrieval
4. Batch processing for efficiency
5. Caching to reduce API costs

LLAMA API Benefits:
- Open-source LLM from Meta
- Cost-effective (free for self-hosted, or pay-per-use APIs)
- Privacy-friendly
- Strong semantic understanding
- Customizable and fine-tunable

Vector Database:
- Pinecone (serverless, managed, recommended)
- Alternative: Weaviate, Milvus

Author: RAG Development Team
Version: 1.1 (Llama API Edition)
Date: 2026-08-14
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import hashlib
import time
from datetime import datetime
import tiktoken
import requests

# Optional imports
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding a text chunk."""
    chunk_id: str
    text: str
    embedding: List[float]
    dimension: int
    model: str
    tokens_used: int
    cost_usd: float
    created_at: str


@dataclass
class EmbeddingConfig:
    """Configuration for embeddings."""
    model: str  # 'llama', 'openai', 'sentence-transformers'
    embedding_model_name: str  # specific model (e.g., 'meta-llama-3-8b', 'text-embedding-3-large')
    api_endpoint: Optional[str] = None  # For Llama API endpoints
    api_key: Optional[str] = None
    batch_size: int = 20
    dimension: int = 1024  # for Llama embeddings (3072 for OpenAI)
    cache_embeddings: bool = True
    cache_dir: str = "./embedding_cache"


class EmbeddingProvider:
    """Base class for embedding providers."""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.cache_dir = config.cache_dir
        self.cache_enabled = config.cache_embeddings

        # Create cache directory
        if self.cache_enabled:
            os.makedirs(self.cache_dir, exist_ok=True)

    def embed(self, text: str) -> EmbeddingResult:
        """Embed a single text chunk."""
        raise NotImplementedError

    def embed_batch(self, texts: List[str], chunk_ids: List[str]) -> List[EmbeddingResult]:
        """Embed multiple text chunks."""
        raise NotImplementedError

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        hash_obj = hashlib.md5(text.encode())
        return hash_obj.hexdigest()

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding if available."""
        if not self.cache_enabled:
            return None

        cache_key = self._get_cache_key(text)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Cache hit for: {text[:50]}...")
                    return data['embedding']
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        return None

    def _cache_embedding(self, text: str, embedding: List[float], metadata: Dict):
        """Cache an embedding."""
        if not self.cache_enabled:
            return

        cache_key = self._get_cache_key(text)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'text': text[:500],
                    'embedding': embedding,
                    'metadata': metadata,
                    'cached_at': datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class LlamaEmbeddingProvider(EmbeddingProvider):
    """
    Llama Embedding Provider

    Why Llama is Great for HR Policies:
    ────────────────────────────────────────────────────────────

    1. OPEN-SOURCE & PRIVACY-FRIENDLY
       ├─ No vendor lock-in
       ├─ Data stays on your servers (self-hosted)
       ├─ No data sent to external APIs
       └─ Full control over embeddings

    2. COST-EFFECTIVE
       ├─ Free for self-hosted deployments
       ├─ $0.01-0.10 per 1M tokens for API services
       ├─ 10-100x cheaper than proprietary solutions
       └─ No per-query costs after model download

    3. HIGH QUALITY
       ├─ Meta's Llama 3/3.1 models have excellent embeddings
       ├─ Strong semantic understanding
       ├─ Good for domain-specific text (policies)
       └─ Competitive with OpenAI for HR use cases

    4. CUSTOMIZABLE
       ├─ Can fine-tune for policy-specific language
       ├─ Adapt to organization terminology
       ├─ No licensing restrictions
       └─ Improve quality over time

    5. COMMUNITY-DRIVEN
       ├─ Large ecosystem of tools
       ├─ Active development and improvements
       ├─ Many deployment options
       └─ Strong community support

    Deployment Options:
    ─────────────────
    1. Self-Hosted (Ollama, vLLM)
       - Cost: $0/month (your infrastructure)
       - Speed: Depends on GPU
       - Privacy: 100% local

    2. API Services (Together AI, Replicate, Modal)
       - Cost: $0.01-0.10 per 1M tokens
       - Speed: Fast (cloud infrastructure)
       - Privacy: Data shared with provider

    3. Hugging Face Endpoints
       - Cost: Variable based on usage
       - Speed: Good
       - Privacy: Depends on configuration

    For HR Policies (RECOMMENDATION):
    ──────────────────────────────────
    → Use Together AI (llama-api.com)
    → Free tier includes embeddings
    → Pay-as-you-go model
    → Easy integration
    """

    def __init__(self, config: EmbeddingConfig, api_key: Optional[str] = None):
        super().__init__(config)

        # Get API endpoint and key
        self.api_endpoint = config.api_endpoint or os.getenv('LLAMA_API_ENDPOINT')
        self.api_key = api_key or config.api_key or os.getenv('LLAMA_API_KEY')

        if not self.api_endpoint or not self.api_key:
            raise ValueError(
                "Llama API endpoint and key required. "
                "Set LLAMA_API_ENDPOINT and LLAMA_API_KEY environment variables, "
                "or pass in config."
            )

        self.model = config.embedding_model_name
        logger.info(f"Llama Embedding Provider initialized with model: {self.model}")
        logger.info(f"API Endpoint: {self.api_endpoint}")

    def embed(self, text: str, chunk_id: str = "default") -> EmbeddingResult:
        """Embed a single text chunk using Llama API."""

        # Check cache
        cached_embedding = self._get_cached_embedding(text)
        if cached_embedding:
            return EmbeddingResult(
                chunk_id=chunk_id,
                text=text,
                embedding=cached_embedding,
                dimension=len(cached_embedding),
                model=self.model,
                tokens_used=0,  # Cached, no tokens used
                cost_usd=0.0,
                created_at=datetime.now().isoformat()
            )

        try:
            # Call Llama API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "input": text,
                "encoding_format": "float"
            }

            response = requests.post(
                f"{self.api_endpoint}/embeddings",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")

            data = response.json()
            embedding = data['data'][0]['embedding']
            tokens_used = data.get('usage', {}).get('prompt_tokens', 0)
            cost = self._calculate_cost(tokens_used)

            # Cache result
            self._cache_embedding(text, embedding, {
                'model': self.model,
                'tokens': tokens_used
            })

            return EmbeddingResult(
                chunk_id=chunk_id,
                text=text,
                embedding=embedding,
                dimension=len(embedding),
                model=self.model,
                tokens_used=tokens_used,
                cost_usd=cost,
                created_at=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Llama API embedding error: {e}")
            raise

    def embed_batch(self, texts: List[str], chunk_ids: List[str]) -> List[EmbeddingResult]:
        """Embed multiple texts efficiently using Llama API."""

        logger.info(f"Embedding batch of {len(texts)} chunks using Llama API")
        results = []
        total_cost = 0.0
        total_tokens = 0

        # Process in batches
        for i in range(0, len(texts), self.config.batch_size):
            batch_texts = texts[i:i + self.config.batch_size]
            batch_ids = chunk_ids[i:i + self.config.batch_size]

            logger.info(f"Processing batch {i // self.config.batch_size + 1}...")

            try:
                # Call Llama API with batch
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "input": batch_texts,
                    "encoding_format": "float"
                }

                response = requests.post(
                    f"{self.api_endpoint}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code != 200:
                    raise Exception(f"API Error: {response.status_code} - {response.text}")

                data = response.json()
                embeddings_data = data['data']
                tokens = data.get('usage', {}).get('prompt_tokens', 0)

                # Process results
                for j, (text, chunk_id) in enumerate(zip(batch_texts, batch_ids)):
                    # Find corresponding embedding
                    embedding_item = next(
                        (item for item in embeddings_data if item['index'] == j),
                        None
                    )

                    if not embedding_item:
                        logger.warning(f"No embedding found for index {j}")
                        continue

                    embedding = embedding_item['embedding']
                    cost = self._calculate_cost(tokens // len(batch_texts))

                    # Cache
                    self._cache_embedding(text, embedding, {'model': self.model})

                    results.append(EmbeddingResult(
                        chunk_id=chunk_id,
                        text=text,
                        embedding=embedding,
                        dimension=len(embedding),
                        model=self.model,
                        tokens_used=tokens // len(batch_texts),
                        cost_usd=cost,
                        created_at=datetime.now().isoformat()
                    ))

                    total_tokens += tokens // len(batch_texts)
                    total_cost += cost

            except Exception as e:
                logger.error(f"Batch embedding error: {e}")
                raise

        logger.info(f"Batch embedding complete. Tokens: {total_tokens}, Cost: ${total_cost:.4f}")
        return results

    def _calculate_cost(self, tokens: int) -> float:
        """
        Calculate cost for Llama API embedding.

        Cost depends on provider:
        - Together AI: $0.10 per 1M tokens (free tier available)
        - Replicate: $0.0001 per 1000 tokens
        - Local (Ollama): $0.00 (your hardware)
        """
        # Together AI pricing: $0.10 per 1M input tokens
        cost_per_million = 0.10
        return (tokens / 1_000_000) * cost_per_million


class PineconeVectorStore:
    """Pinecone Vector Database Integration (same as before)."""

    def __init__(self, api_key: Optional[str] = None, index_name: str = "hr-policies"):
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone SDK not installed. Install with: pip install pinecone-client")

        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("Pinecone API key required. Set PINECONE_API_KEY env var.")

        self.index_name = index_name

        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment="gcp-starter")

        # Get or create index
        self._ensure_index_exists()
        self.index = pinecone.Index(index_name)

        logger.info(f"Pinecone initialized with index: {index_name}")

    def _ensure_index_exists(self):
        """Ensure the index exists, create if needed."""
        indexes = pinecone.list_indexes()

        if self.index_name not in indexes:
            logger.info(f"Creating index: {self.index_name}")
            pinecone.create_index(
                name=self.index_name,
                dimension=1024,  # For Llama embeddings (adjust if using different model)
                metric="cosine"
            )
            logger.info(f"Index created: {self.index_name}")
        else:
            logger.info(f"Index already exists: {self.index_name}")

    def upsert_embeddings(
        self,
        embeddings: List[EmbeddingResult],
        batch_size: int = 100
    ) -> Dict:
        """Upload embeddings to Pinecone."""
        logger.info(f"Upserting {len(embeddings)} embeddings to Pinecone")

        vectors_to_upsert = []
        total_upserted = 0
        total_cost = 0.0

        for result in embeddings:
            vector_tuple = (
                result.chunk_id,
                result.embedding,
                {
                    "text": result.text[:1000],
                    "model": result.model,
                    "created_at": result.created_at,
                    "tokens_used": result.tokens_used
                }
            )
            vectors_to_upsert.append(vector_tuple)
            total_cost += result.cost_usd

            # Batch upsert
            if len(vectors_to_upsert) >= batch_size:
                self.index.upsert(vectors=vectors_to_upsert)
                total_upserted += len(vectors_to_upsert)
                logger.info(f"Upserted batch: {total_upserted} vectors")
                vectors_to_upsert = []

        # Upsert remaining vectors
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
            total_upserted += len(vectors_to_upsert)

        # Get index stats
        stats = self.index.describe_index_stats()

        return {
            "total_upserted": total_upserted,
            "total_vectors": stats.get('total_vector_count', 0),
            "total_cost_usd": total_cost,
            "index_stats": stats
        }

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search Pinecone index for similar vectors."""
        logger.info(f"Searching Pinecone with top_k={top_k}")

        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=metadata_filter
            )

            search_results = []
            for match in results.get('matches', []):
                search_results.append({
                    'chunk_id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {})
                })

            logger.info(f"Found {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    def delete_index(self):
        """Delete the index (use with caution!)."""
        logger.warning(f"Deleting index: {self.index_name}")
        pinecone.delete_index(self.index_name)


class LlamaEmbeddingAndVectorPipeline:
    """Complete pipeline for Llama embeddings and vector storage."""

    def __init__(
        self,
        embedding_config: EmbeddingConfig,
        pinecone_api_key: Optional[str] = None,
        pinecone_index: str = "hr-policies"
    ):
        """Initialize the Llama embedding and vector pipeline."""

        # Initialize Llama embedding provider
        self.embedding_provider = LlamaEmbeddingProvider(embedding_config)

        # Initialize vector store
        self.vector_store = PineconeVectorStore(
            api_key=pinecone_api_key,
            index_name=pinecone_index
        )

        self.config = embedding_config
        logger.info("Llama Embedding and Vector Pipeline initialized")

    def process_chunks(self, chunks: List) -> Dict:
        """Process a list of chunks through the complete pipeline."""
        logger.info(f"Processing {len(chunks)} chunks through pipeline")

        # Extract texts and IDs
        texts = [chunk.text for chunk in chunks]
        chunk_ids = [f"chunk_{chunk.chunk_number}_{hash(chunk.text)[:8]}" for chunk in chunks]

        # Generate embeddings
        start_time = time.time()
        embeddings = self.embedding_provider.embed_batch(texts, chunk_ids)
        embedding_time = time.time() - start_time

        # Store in vector database
        start_time = time.time()
        upsert_stats = self.vector_store.upsert_embeddings(embeddings)
        upsert_time = time.time() - start_time

        # Calculate statistics
        total_cost = sum(e.cost_usd for e in embeddings)
        total_tokens = sum(e.tokens_used for e in embeddings)

        stats = {
            "chunks_processed": len(chunks),
            "embeddings_created": len(embeddings),
            "total_cost_usd": total_cost,
            "total_tokens_used": total_tokens,
            "embedding_time_seconds": embedding_time,
            "upsert_time_seconds": upsert_time,
            "total_time_seconds": embedding_time + upsert_time,
            "vector_store_stats": upsert_stats,
            "avg_cost_per_chunk": total_cost / len(chunks) if chunks else 0,
            "avg_tokens_per_chunk": total_tokens // len(chunks) if chunks else 0
        }

        logger.info(f"Pipeline complete. Stats: {stats}")
        return stats

    def search_similar(
        self,
        query_text: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Search for similar chunks given a query."""
        # Generate embedding for query
        query_result = self.embedding_provider.embed(query_text, chunk_id="query")
        query_embedding = query_result.embedding

        # Search in vector database
        results = self.vector_store.search(query_embedding, top_k=top_k)

        return results


def demonstrate_llama_embedding_pipeline():
    """Demonstrate the Llama embedding and vector pipeline."""

    print("\n" + "=" * 80)
    print("LLAMA EMBEDDING AND VECTOR STORAGE PIPELINE DEMONSTRATION")
    print("=" * 80 + "\n")

    print("1️⃣  LLAMA API CONFIGURATION")
    print("-" * 80)

    config = EmbeddingConfig(
        model="llama",
        embedding_model_name="meta-llama-3-8b-instruct",
        api_endpoint="https://api.together.xyz/v1",  # Together AI
        batch_size=20,
        dimension=1024,
        cache_embeddings=True
    )

    print(f"Model: {config.model}")
    print(f"Embedding Model: {config.embedding_model_name}")
    print(f"API Endpoint: {config.api_endpoint}")
    print(f"Dimension: {config.dimension}")
    print(f"Batch Size: {config.batch_size}")
    print(f"Caching: {config.cache_embeddings}\n")

    print("2️⃣  WHY LLAMA API FOR HR POLICIES")
    print("-" * 80)

    benefits = [
        ("Open Source", "No vendor lock-in, full control over embeddings"),
        ("Privacy", "Self-hosted option keeps data on your servers"),
        ("Cost", "$0.10/1M tokens or $0 for self-hosted"),
        ("Quality", "Strong semantic understanding of policy language"),
        ("Customizable", "Can fine-tune for domain-specific terminology"),
        ("Community", "Large ecosystem and active development"),
    ]

    for benefit, description in benefits:
        print(f"  ✓ {benefit:20} : {description}")

    print("\n3️⃣  DEPLOYMENT OPTIONS")
    print("-" * 80)

    options = [
        ("Together AI (Recommended)", "API endpoint", "Fast", "$0.10/1M tokens", "Easy"),
        ("Ollama (Self-hosted)", "Local GPU", "Variable", "$0", "Medium"),
        ("Replicate", "API endpoint", "Fast", "$0.0001/1K tokens", "Easy"),
        ("Hugging Face", "API endpoint", "Good", "Variable", "Easy"),
    ]

    print("\nOption                   | Type        | Speed    | Cost            | Setup")
    print("─" * 80)
    for opt, typ, speed, cost, setup in options:
        print(f"{opt:24} | {typ:11} | {speed:8} | {cost:15} | {setup}")

    print("\n4️⃣  COST ANALYSIS: LLAMA VS OPENAI")
    print("-" * 80)

    print("\nFor 30 HR Policy Documents (120,000 tokens):\n")

    comparison = [
        ("Llama (Together AI)", "$0.012", "1024", "10 min"),
        ("Llama (Self-hosted)", "$0.000", "1024", "Variable"),
        ("OpenAI Large", "$0.016", "3072", "2 min"),
        ("OpenAI Small", "$0.003", "1536", "2 min"),
    ]

    print("Provider                 | Cost      | Dimensions | Speed")
    print("─" * 60)
    for provider, cost, dims, speed in comparison:
        print(f"{provider:24} | {cost:9} | {dims:10} | {speed}")

    print("\n5️⃣  LLAMA API SETUP (TOGETHER AI - RECOMMENDED)")
    print("-" * 80)

    setup_steps = [
        ("1. Sign up", "https://www.together.ai (free tier available)"),
        ("2. Get API Key", "Copy from Together AI dashboard"),
        ("3. Set environment", "export LLAMA_API_KEY='your-key'"),
        ("4. Install SDK", "pip install requests"),
        ("5. Test", "Run this script with LLAMA_API_KEY set"),
    ]

    for step, action in setup_steps:
        print(f"  {step:20} : {action}")

    print("\n6️⃣  INTEGRATION EXAMPLE")
    print("-" * 80)

    integration_code = '''
from embedding_module_llama import LlamaEmbeddingAndVectorPipeline, EmbeddingConfig

# Configure Llama embeddings
config = EmbeddingConfig(
    model="llama",
    embedding_model_name="meta-llama-3-8b-instruct",
    api_endpoint="https://api.together.xyz/v1",
    api_key="your-together-ai-key",
    batch_size=20,
    dimension=1024
)

# Initialize pipeline
pipeline = LlamaEmbeddingAndVectorPipeline(
    embedding_config=config,
    pinecone_api_key="your-pinecone-key"
)

# Process chunks
stats = pipeline.process_chunks(chunks)
print(f"Cost: ${stats['total_cost_usd']:.4f}")

# Search
results = pipeline.search_similar("How do I request remote work?", top_k=5)
    '''

    print(integration_code)

    print("\n" + "=" * 80)
    print("LLAMA API IS PERFECT FOR HR POLICIES")
    print("=" * 80 + "\n")

    print("✓ Open-source = no vendor lock-in")
    print("✓ Privacy = optional self-hosted deployment")
    print("✓ Cost = $0-0.10/1M tokens vs $0.13 for OpenAI")
    print("✓ Quality = competitive with proprietary models")
    print("✓ Customizable = can fine-tune for your organization")
    print("\nRecommendation: Use Together AI for easy setup + cost savings\n")


if __name__ == "__main__":
    """Run demonstration of Llama embedding pipeline."""
    demonstrate_llama_embedding_pipeline()

    print("=" * 80)
    print("SETUP INSTRUCTIONS FOR TOGETHER AI (RECOMMENDED)")
    print("=" * 80 + "\n")

    setup_guide = '''
STEP 1: Create Together AI Account
────────────────────────────────────
1. Go to https://www.together.ai
2. Sign up for free account
3. Get API key from dashboard

STEP 2: Install Dependencies
──────────────────────────────
$ pip install requests pinecone-client

STEP 3: Set Environment Variables
──────────────────────────────────
$ export LLAMA_API_KEY="your-together-ai-key"
$ export LLAMA_API_ENDPOINT="https://api.together.xyz/v1"
$ export PINECONE_API_KEY="your-pinecone-key"

STEP 4: Use in Your Project
────────────────────────────
from embedding_module_llama import LlamaEmbeddingAndVectorPipeline, EmbeddingConfig

config = EmbeddingConfig(
    model="llama",
    embedding_model_name="meta-llama-3-8b-instruct",
    api_endpoint=os.getenv("LLAMA_API_ENDPOINT"),
    api_key=os.getenv("LLAMA_API_KEY")
)

pipeline = LlamaEmbeddingAndVectorPipeline(
    embedding_config=config,
    pinecone_api_key=os.getenv("PINECONE_API_KEY")
)

# Process your documents
stats = pipeline.process_chunks(chunks)

STEP 5: Verify It Works
───────────────────────
Results should show:
✓ Embeddings created successfully
✓ Low cost (~$0.00012 per 1000 tokens)
✓ Stored in Pinecone
✓ Ready for semantic search

TOGETHER AI PRICING
───────────────────
Free tier: Generous free credits
Pay-as-you-go: $0.10 per 1M input tokens
No setup fees, no minimum commitment

ALTERNATIVE: SELF-HOSTED WITH OLLAMA
────────────────────────────────────
If you want $0 cost with local GPU:

1. Install Ollama: https://ollama.ai
2. Pull Llama model: ollama pull llama2
3. Run local endpoint: ollama serve
4. Update API endpoint to http://localhost:11434

Cost: $0 (just electricity)
Speed: Depends on your GPU
Privacy: 100% local
    '''

    print(setup_guide)
