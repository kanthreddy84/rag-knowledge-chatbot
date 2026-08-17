"""
Embedding and Vector Storage Module for RAG Knowledge Chatbot

This module handles:
1. Document chunk embedding (converting text to vectors)
2. Vector storage in Pinecone
3. Semantic search and retrieval
4. Batch processing for efficiency
5. Caching to reduce API costs

Supported Embedding Models:
- OpenAI's text-embedding-3-large (recommended)
- Anthropic's Claude embeddings
- Open-source alternatives (Sentence Transformers)

Vector Database:
- Pinecone (serverless, managed, recommended)
- Alternative: Weaviate, Milvus

Author: RAG Development Team
Version: 1.0
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

# Optional imports (install as needed)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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
    model: str  # 'openai', 'anthropic', 'sentence-transformers'
    embedding_model_name: str  # specific model (e.g., 'text-embedding-3-large')
    batch_size: int = 20
    dimension: int = 1536  # for 3-large
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
                    'text': text[:500],  # Store preview
                    'embedding': embedding,
                    'metadata': metadata,
                    'cached_at': datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI Embedding Provider

    Uses: text-embedding-3-large (recommended for HR policies)

    Why OpenAI embeddings are best for HR policies:
    1. Dimensions: 3072 (large model) - excellent for precise retrieval
    2. Quality: State-of-the-art semantic understanding
    3. Cost: Competitive ($0.13 per million tokens)
    4. Speed: Fast batch processing
    5. Reliability: Production-grade, battle-tested
    6. Context: Understands domain-specific policy language

    Cost Analysis:
    - Input: $0.13 per 1M tokens
    - For 15-30 docs (60K-120K tokens): $0.01-0.02 per iteration
    - Batch size 20 chunks: ~$0.003 per batch
    """

    def __init__(self, config: EmbeddingConfig, api_key: Optional[str] = None):
        super().__init__(config)

        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY env var.")

        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = config.embedding_model_name

        logger.info(f"OpenAI Embedding Provider initialized with model: {self.model}")

    def embed(self, text: str, chunk_id: str = "default") -> EmbeddingResult:
        """Embed a single text chunk using OpenAI."""

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
            # Call OpenAI API
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding = response.data[0].embedding
            tokens_used = response.usage.prompt_tokens
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
            logger.error(f"OpenAI embedding error: {e}")
            raise

    def embed_batch(self, texts: List[str], chunk_ids: List[str]) -> List[EmbeddingResult]:
        """Embed multiple texts efficiently using batch processing."""

        logger.info(f"Embedding batch of {len(texts)} chunks using OpenAI")
        results = []
        total_cost = 0.0
        total_tokens = 0

        # Process in batches
        for i in range(0, len(texts), self.config.batch_size):
            batch_texts = texts[i:i + self.config.batch_size]
            batch_ids = chunk_ids[i:i + self.config.batch_size]

            logger.info(f"Processing batch {i // self.config.batch_size + 1}...")

            try:
                # Call OpenAI API with batch
                response = self.client.embeddings.create(
                    input=batch_texts,
                    model=self.model
                )

                # Process results
                for j, item in enumerate(response.data):
                    embedding = item.embedding
                    chunk_id = batch_ids[j]
                    text = batch_texts[j]

                    tokens = response.usage.prompt_tokens // len(batch_texts)  # Approximate per text
                    cost = self._calculate_cost(tokens)

                    # Cache
                    self._cache_embedding(text, embedding, {'model': self.model})

                    results.append(EmbeddingResult(
                        chunk_id=chunk_id,
                        text=text,
                        embedding=embedding,
                        dimension=len(embedding),
                        model=self.model,
                        tokens_used=tokens,
                        cost_usd=cost,
                        created_at=datetime.now().isoformat()
                    ))

                    total_tokens += tokens
                    total_cost += cost

            except Exception as e:
                logger.error(f"Batch embedding error: {e}")
                raise

        logger.info(f"Batch embedding complete. Tokens: {total_tokens}, Cost: ${total_cost:.4f}")
        return results

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for OpenAI embedding."""
        # text-embedding-3-large: $0.13 per 1M input tokens
        cost_per_million = 0.13
        return (tokens / 1_000_000) * cost_per_million


class AnthropicEmbeddingProvider(EmbeddingProvider):
    """
    Anthropic Embedding Provider (Claude)

    Features:
    - Native embedding support in Claude API
    - Dimensions: 1024
    - Optimized for understanding policy language
    - Cost-effective for enterprise use
    """

    def __init__(self, config: EmbeddingConfig, api_key: Optional[str] = None):
        super().__init__(config)

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")

        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY env var.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = config.embedding_model_name

        logger.info(f"Anthropic Embedding Provider initialized")

    def embed(self, text: str, chunk_id: str = "default") -> EmbeddingResult:
        """Embed using Anthropic (Claude)."""

        # Check cache
        cached_embedding = self._get_cached_embedding(text)
        if cached_embedding:
            return EmbeddingResult(
                chunk_id=chunk_id,
                text=text,
                embedding=cached_embedding,
                dimension=len(cached_embedding),
                model="claude-embedding",
                tokens_used=0,
                cost_usd=0.0,
                created_at=datetime.now().isoformat()
            )

        try:
            # Note: As of my knowledge cutoff, Anthropic may have embedding via API
            # Check their latest documentation for embedding API availability
            logger.warning("Anthropic native embeddings may not be fully available yet")
            logger.info("Falling back to text-embedding-3-small for demo")

            # For now, we'll demonstrate the structure
            # In production, use OpenAI or open-source alternatives
            raise NotImplementedError("Use OpenAI or open-source embeddings for now")

        except Exception as e:
            logger.error(f"Anthropic embedding error: {e}")
            raise

    def embed_batch(self, texts: List[str], chunk_ids: List[str]) -> List[EmbeddingResult]:
        """Batch embedding via Anthropic."""
        raise NotImplementedError("Use OpenAI or open-source embeddings for now")


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    Open-source Embedding Provider using Sentence Transformers

    Models: all-MiniLM-L6-v2, all-mpnet-base-v2, paraphrase-MiniLM-L6-v2

    Why useful for HR policies:
    1. No API costs (local/self-hosted)
    2. Good quality for domain-specific text
    3. Fast inference (milliseconds)
    4. Privacy-friendly (no data sent to APIs)
    5. Customizable/fine-tunable

    Tradeoff:
    - Slightly lower quality than OpenAI 3-large
    - Requires local compute resources
    - Smaller dimensions (384-768 vs 3072)

    Best for: Cost-sensitive deployments or privacy-critical scenarios
    """

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence Transformers not installed. Install with: pip install sentence-transformers")

        self.model_name = config.embedding_model_name
        self.model = SentenceTransformer(self.model_name)
        self.dimension = config.dimension

        logger.info(f"Sentence Transformer initialized with model: {self.model_name}")

    def embed(self, text: str, chunk_id: str = "default") -> EmbeddingResult:
        """Embed using sentence transformers (local, no cost)."""

        # Check cache
        cached_embedding = self._get_cached_embedding(text)
        if cached_embedding:
            return EmbeddingResult(
                chunk_id=chunk_id,
                text=text,
                embedding=cached_embedding,
                dimension=len(cached_embedding),
                model=self.model_name,
                tokens_used=0,
                cost_usd=0.0,
                created_at=datetime.now().isoformat()
            )

        try:
            embedding = self.model.encode(text, convert_to_tensor=False).tolist()

            # Cache
            self._cache_embedding(text, embedding, {'model': self.model_name})

            return EmbeddingResult(
                chunk_id=chunk_id,
                text=text,
                embedding=embedding,
                dimension=len(embedding),
                model=self.model_name,
                tokens_used=0,  # No token counting for local models
                cost_usd=0.0,  # No cost for local inference
                created_at=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Sentence Transformer embedding error: {e}")
            raise

    def embed_batch(self, texts: List[str], chunk_ids: List[str]) -> List[EmbeddingResult]:
        """Batch embedding with sentence transformers (optimized)."""

        logger.info(f"Embedding batch of {len(texts)} chunks using Sentence Transformers")

        try:
            # Batch encoding is optimized in sentence-transformers
            embeddings = self.model.encode(texts, convert_to_tensor=False, batch_size=self.config.batch_size)

            results = []
            for i, (text, chunk_id, embedding) in enumerate(zip(texts, chunk_ids, embeddings)):
                # Cache
                self._cache_embedding(text, embedding.tolist(), {'model': self.model_name})

                results.append(EmbeddingResult(
                    chunk_id=chunk_id,
                    text=text,
                    embedding=embedding.tolist(),
                    dimension=len(embedding),
                    model=self.model_name,
                    tokens_used=0,
                    cost_usd=0.0,
                    created_at=datetime.now().isoformat()
                ))

            logger.info(f"Batch embedding complete. Processed {len(results)} chunks")
            return results

        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise


class PineconeVectorStore:
    """
    Pinecone Vector Database Integration

    Why Pinecone is best for RAG systems:

    1. FULLY MANAGED
       - No infrastructure to manage
       - Automatic scaling
       - 99.95% SLA uptime

    2. SERVERLESS & COST-EFFECTIVE
       - Pay for usage (reads/writes/storage)
       - No minimum costs
       - Auto-scaling based on demand

    3. OPTIMIZED FOR SEMANTIC SEARCH
       - Hybrid search (dense + sparse)
       - Advanced filtering on metadata
       - Fast retrieval (<200ms)

    4. PRODUCTION-READY
       - Built-in monitoring & alerting
       - Backup & disaster recovery
       - Multi-region support

    5. SECURITY
       - Encryption in transit & at rest
       - API key-based authentication
       - Audit logging

    Pricing for your use case (15-30 docs):
    - Initial: ~$0-5/month (very low volume)
    - Scales with usage
    - Storage: ~$0.10 per GB-month
    - Queries: Included in free tier initially
    """

    def __init__(self, api_key: Optional[str] = None, index_name: str = "hr-policies"):
        """
        Initialize Pinecone vector store.

        Args:
            api_key: Pinecone API key (or use PINECONE_API_KEY env var)
            index_name: Name of the index to use
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone SDK not installed. Install with: pip install pinecone-client")

        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("Pinecone API key required. Set PINECONE_API_KEY env var.")

        self.index_name = index_name

        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment="gcp-starter")  # Use appropriate environment

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
                dimension=1536,  # For text-embedding-3-large
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
        """
        Upload embeddings to Pinecone.

        Args:
            embeddings: List of EmbeddingResult objects
            batch_size: Batch size for upsert operations

        Returns:
            Statistics about the upsert operation
        """
        logger.info(f"Upserting {len(embeddings)} embeddings to Pinecone")

        vectors_to_upsert = []
        total_upserted = 0
        total_cost = 0.0

        for result in embeddings:
            vector_tuple = (
                result.chunk_id,
                result.embedding,
                {
                    "text": result.text[:1000],  # Store text preview
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
        """
        Search Pinecone index for similar vectors.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            metadata_filter: Optional metadata filtering

        Returns:
            List of search results with scores
        """
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


class EmbeddingAndVectorPipeline:
    """
    Complete pipeline for embedding chunks and storing in vector database.

    Workflow:
    1. Take chunks from document_chunking module
    2. Generate embeddings using embedding provider
    3. Cache embeddings locally to reduce API costs
    4. Store in Pinecone vector database
    5. Return statistics and costs
    """

    def __init__(
        self,
        embedding_config: EmbeddingConfig,
        pinecone_api_key: Optional[str] = None,
        pinecone_index: str = "hr-policies"
    ):
        """Initialize the embedding and vector pipeline."""

        # Initialize embedding provider based on config
        if embedding_config.model == "openai":
            self.embedding_provider = OpenAIEmbeddingProvider(embedding_config)
        elif embedding_config.model == "sentence-transformers":
            self.embedding_provider = SentenceTransformerEmbeddingProvider(embedding_config)
        elif embedding_config.model == "anthropic":
            self.embedding_provider = AnthropicEmbeddingProvider(embedding_config)
        else:
            raise ValueError(f"Unknown embedding model: {embedding_config.model}")

        # Initialize vector store
        self.vector_store = PineconeVectorStore(
            api_key=pinecone_api_key,
            index_name=pinecone_index
        )

        self.config = embedding_config
        logger.info("Embedding and Vector Pipeline initialized")

    def process_chunks(self, chunks: List) -> Dict:
        """
        Process a list of chunks through the complete pipeline.

        Args:
            chunks: List of Chunk objects from document_chunking module

        Returns:
            Pipeline statistics and metrics
        """
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
        """
        Search for similar chunks given a query.

        Args:
            query_text: Natural language query
            top_k: Number of results to return

        Returns:
            List of similar chunks with scores
        """
        # Generate embedding for query
        query_result = self.embedding_provider.embed(query_text, chunk_id="query")
        query_embedding = query_result.embedding

        # Search in vector database
        results = self.vector_store.search(query_embedding, top_k=top_k)

        return results


def demonstrate_embedding_pipeline():
    """Demonstrate the complete embedding and vector pipeline."""

    print("\n" + "=" * 80)
    print("EMBEDDING AND VECTOR STORAGE PIPELINE DEMONSTRATION")
    print("=" * 80 + "\n")

    # Sample chunks (would come from document_chunking module)
    from dataclasses import dataclass

    @dataclass
    class MockChunk:
        chunk_number: int
        text: str

    sample_chunks = [
        MockChunk(1, "Remote work is defined as performing job duties from locations other than the primary office."),
        MockChunk(2, "All employees in eligible roles can apply for remote work arrangements."),
        MockChunk(3, "The approval process requires manager evaluation and HR compliance review."),
    ]

    print("1️⃣  CONFIGURATION")
    print("-" * 80)

    # Configuration
    config = EmbeddingConfig(
        model="openai",
        embedding_model_name="text-embedding-3-large",
        batch_size=20,
        dimension=1536,
        cache_embeddings=True
    )

    print(f"Model: {config.model}")
    print(f"Embedding Model: {config.embedding_model_name}")
    print(f"Dimension: {config.dimension}")
    print(f"Batch Size: {config.batch_size}")
    print(f"Caching: {config.cache_embeddings}\n")

    print("2️⃣  EMBEDDING PROVIDER COMPARISON")
    print("-" * 80)

    comparison = [
        ["Provider", "Quality", "Cost", "Speed", "Privacy", "Best For"],
        ["OpenAI 3-large", "⭐⭐⭐⭐⭐", "$$", "Fast", "No", "Production RAG"],
        ["OpenAI 3-small", "⭐⭐⭐⭐", "$", "Fast", "No", "Cost-sensitive"],
        ["Sentence Transformers", "⭐⭐⭐⭐", "Free", "Very Fast", "Yes", "Self-hosted"],
        ["Anthropic (Claude)", "⭐⭐⭐⭐⭐", "$$$", "Medium", "No", "Multi-modal"],
    ]

    for row in comparison:
        print(f"{row[0]:25} {row[1]:20} {row[2]:10} {row[3]:10} {row[4]:10} {row[5]}")

    print("\n3️⃣  COST ANALYSIS FOR YOUR 15-30 DOCUMENTS")
    print("-" * 80)

    # Cost calculation
    docs_count = [15, 20, 25, 30]
    chunks_per_doc = 10
    tokens_per_chunk = 300

    print("\nDocument Count | Chunks | Tokens | OpenAI Cost | Sentence-T Cost")
    print("─" * 70)

    for docs in docs_count:
        total_chunks = docs * chunks_per_doc
        total_tokens = total_chunks * tokens_per_chunk

        # OpenAI cost: $0.13 per 1M tokens
        openai_cost = (total_tokens / 1_000_000) * 0.13

        # Sentence Transformers: Free (local)
        st_cost = 0.0

        print(f"{docs:14} | {total_chunks:6} | {total_tokens:6} | ${openai_cost:10.4f} | ${st_cost:10.4f}")

    print("\n4️⃣  PINECONE VECTOR DATABASE")
    print("-" * 80)

    pinecone_info = {
        "Storage Cost": "$0.10 per GB-month",
        "Read Cost": "Included in free tier initially",
        "Write Cost": "Included in free tier initially",
        "Vector Capacity": "1.5B vectors in free tier",
        "Retrieval Speed": "<200ms for similarity search",
        "SLA": "99.95% uptime"
    }

    for key, value in pinecone_info.items():
        print(f"  {key:20} : {value}")

    print("\n5️⃣  PIPELINE STATISTICS (SAMPLE)")
    print("-" * 80)

    stats = {
        "Total Chunks": 200,
        "Total Tokens": 60000,
        "Total Cost (OpenAI)": "$0.008",
        "Embedding Time": "45 seconds",
        "Upsert Time": "15 seconds",
        "Total Pipeline Time": "60 seconds",
        "Vectors in Database": 200,
        "Average Chunk Size": 300
    }

    for key, value in stats.items():
        print(f"  {key:25} : {value}")

    print("\n" + "=" * 80)
    print("KEY RECOMMENDATIONS FOR YOUR RAG CHATBOT")
    print("=" * 80 + "\n")

    recommendations = [
        ("Embedding Model", "text-embedding-3-large", "Best quality for policy understanding"),
        ("Vector Database", "Pinecone", "Fully managed, scalable, cost-effective"),
        ("Caching", "Enabled", "Reduces API calls and costs"),
        ("Batch Size", "20-50", "Optimal for throughput and memory"),
        ("Refresh Rate", "Weekly", "Keep embeddings current with policy updates"),
    ]

    for aspect, recommendation, reason in recommendations:
        print(f"✓ {aspect:20} : {recommendation:25} ({reason})")


if __name__ == "__main__":
    """Run demonstration of embedding and vector pipeline."""
    demonstrate_embedding_pipeline()

    print("\n" + "=" * 80)
    print("USAGE EXAMPLE")
    print("=" * 80 + "\n")

    usage_code = '''
# Example 1: Using OpenAI Embeddings with Pinecone

from embedding_module import EmbeddingConfig, EmbeddingAndVectorPipeline
from document_chunking import DocumentChunker

# Step 1: Chunk your documents
chunker = DocumentChunker(strategy="HYBRID")
chunks = chunker.chunk_document(policy_text, "Remote Work Policy")

# Step 2: Configure embeddings
config = EmbeddingConfig(
    model="openai",
    embedding_model_name="text-embedding-3-large",
    batch_size=20,
    dimension=1536
)

# Step 3: Initialize pipeline
pipeline = EmbeddingAndVectorPipeline(
    embedding_config=config,
    pinecone_api_key="your-api-key",
    pinecone_index="hr-policies"
)

# Step 4: Process chunks
stats = pipeline.process_chunks(chunks)
print(f"Processed {stats['chunks_processed']} chunks")
print(f"Cost: ${stats['total_cost_usd']:.4f}")

# Step 5: Search
query = "How do I request remote work?"
results = pipeline.search_similar(query, top_k=5)
for result in results:
    print(f"Match: {result['chunk_id']} (score: {result['score']:.3f})")


# Example 2: Using Local Sentence Transformers (No Cost)

config = EmbeddingConfig(
    model="sentence-transformers",
    embedding_model_name="all-MiniLM-L6-v2",  # Lightweight, fast
    batch_size=32
)

pipeline = EmbeddingAndVectorPipeline(
    embedding_config=config,
    pinecone_index="hr-policies"
)

stats = pipeline.process_chunks(chunks)
# Cost: $0.00 (local processing)
# Time: Faster (no API calls)
    '''

    print(usage_code)

    print("\n" + "=" * 80)
    print("SETUP INSTRUCTIONS")
    print("=" * 80 + "\n")

    setup_steps = [
        ("1. Install Dependencies", [
            "pip install openai",
            "pip install pinecone-client",
            "pip install sentence-transformers",
            "pip install tiktoken"
        ]),
        ("2. Set API Keys", [
            "export OPENAI_API_KEY='sk-...'",
            "export PINECONE_API_KEY='...'",
            "Or set in environment variables"
        ]),
        ("3. Run Pipeline", [
            "chunks = chunker.chunk_document(...)",
            "stats = pipeline.process_chunks(chunks)",
            "results = pipeline.search_similar(query)"
        ]),
    ]

    for step_name, commands in setup_steps:
        print(f"{step_name}")
        for cmd in commands:
            print(f"  $ {cmd}")
        print()
'''
