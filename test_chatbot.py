#!/usr/bin/env python3
"""
RAG Chatbot Testing Script
Tests the complete chatbot pipeline with sample HR policy documents

Usage:
    python test_chatbot.py              # Test with all default queries
    python test_chatbot.py --free       # Test with FREE setup (Ollama + FAISS)
    python test_chatbot.py --hybrid     # Test with HYBRID setup (Claude + Pinecone)
"""

import os
import sys
from pathlib import Path
from document_chunking import DocumentChunker

def test_document_processing():
    """Test document chunking"""
    print("\n" + "="*80)
    print("STEP 1: DOCUMENT PROCESSING")
    print("="*80)

    data_folder = Path("sample_data")

    if not data_folder.exists():
        print("❌ ERROR: sample_data folder not found!")
        print("   Create sample_data folder and add HR policy documents")
        return None

    policy_files = list(data_folder.glob("*.txt"))

    if not policy_files:
        print("❌ ERROR: No .txt files found in sample_data folder!")
        print("   Add HR policy documents to sample_data/")
        return None

    print(f"\n✅ Found {len(policy_files)} policy documents:")
    for file in policy_files:
        print(f"   • {file.name}")

    # Process documents
    chunker = DocumentChunker(chunk_size=400, overlap=75, strategy="HYBRID")
    all_chunks = []

    for file_path in policy_files:
        print(f"\n📄 Processing: {file_path.name}")
        chunks = chunker.chunk_document(str(file_path))
        all_chunks.extend(chunks)
        print(f"   ✅ Created {len(chunks)} chunks")

    print(f"\n✅ Total chunks created: {len(all_chunks)}")
    return all_chunks


def test_embedding_free(chunks):
    """Test with FREE setup (sentence-transformers + FAISS)"""
    print("\n" + "="*80)
    print("STEP 2: EMBEDDING (FREE - sentence-transformers + FAISS)")
    print("="*80)

    try:
        from embedding_module_free import FreeEmbeddingProvider
        print("\n✅ Loaded FREE embedding provider (sentence-transformers)")
    except ImportError:
        print("❌ embedding_module_free.py not found!")
        print("   See FREE_SETUP_GUIDE.md for setup instructions")
        return None

    print("\n📥 Initializing embeddings (downloads ~130MB model on first run)...")
    embedder = FreeEmbeddingProvider()

    print("🔄 Embedding chunks...")
    embedder.embed_chunks(chunks)

    print("✅ Embedding complete!")
    return embedder


def test_embedding_hybrid(chunks):
    """Test with HYBRID setup (sentence-transformers + Pinecone + Claude)"""
    print("\n" + "="*80)
    print("STEP 2: EMBEDDING (HYBRID - sentence-transformers + Pinecone)")
    print("="*80)

    try:
        from embedding_module_llama import LlamaEmbeddingAndVectorPipeline, EmbeddingConfig
        print("✅ Loaded embedding module")
    except ImportError:
        print("❌ embedding_module_llama.py not found!")
        return None

    # Check for API keys
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ ERROR: PINECONE_API_KEY not set!")
        print("   Set environment variable: export PINECONE_API_KEY=your_key")
        return None

    print("🔄 Initializing Pinecone...")
    config = EmbeddingConfig(
        model="llama",
        api_key=os.getenv("TOGETHER_API_KEY", "")
    )

    pipeline = LlamaEmbeddingAndVectorPipeline(config)
    print("✅ Embedding pipeline initialized!")
    return pipeline


def test_queries_free(embedder):
    """Test queries with FREE setup"""
    print("\n" + "="*80)
    print("STEP 3: TEST QUERIES (FREE SETUP)")
    print("="*80)

    test_queries = [
        "How much vacation time do I get?",
        "Can I work remotely full-time?",
        "What is the dress code?",
        "How do I report harassment?",
        "Can I carry over unused PTO?",
    ]

    print("\n🤖 Testing queries with FREE setup (Ollama LLM)...")
    print("   Note: Ollama must be running: ollama serve")

    try:
        from llm_module_free import OllamaAnswerGenerator
        generator = OllamaAnswerGenerator(model="llama2")
    except ImportError:
        print("❌ llm_module_free.py not found!")
        print("   See FREE_SETUP_GUIDE.md for Ollama setup")
        return
    except Exception as e:
        print(f"❌ ERROR: Could not connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Query {i}: {query}")
        print(f"{'─'*80}")

        # Search for similar chunks
        results = embedder.search_similar(query, top_k=3)

        if not results:
            print("❌ No similar chunks found!")
            continue

        # Build context
        context = "\n\n".join([
            f"Section: {r['chunk'].section_path}\n{r['chunk'].text}"
            for r in results
        ])

        # Generate answer
        answer_data = generator.generate_answer(query, context)

        print(f"\n✅ Answer:")
        print(f"{answer_data['answer']}")
        print(f"\nCost: ${answer_data.get('cost', 0.0):.4f}")
        print(f"Model: {answer_data.get('model', 'ollama')}")


def test_queries_hybrid(embedder):
    """Test queries with HYBRID setup"""
    print("\n" + "="*80)
    print("STEP 3: TEST QUERIES (HYBRID SETUP)")
    print("="*80)

    # Check for API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not set!")
        print("   Set environment variable: export ANTHROPIC_API_KEY=your_key")
        return

    test_queries = [
        "How much vacation time do I get?",
        "Can I work remotely full-time?",
        "What is the dress code?",
        "How do I report harassment?",
        "Can I carry over unused PTO?",
    ]

    print("\n🤖 Testing queries with HYBRID setup (Claude + Pinecone)...")

    try:
        from llm_answer_generation import LLMConfig, RAGAnswerGenerator
        config = LLMConfig(
            model="claude",
            api_key=anthropic_key
        )
        generator = RAGAnswerGenerator(config)
    except ImportError:
        print("❌ llm_answer_generation.py not found!")
        return
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Query {i}: {query}")
        print(f"{'─'*80}")

        # Search for similar chunks
        results = embedder.search_similar(query, top_k=3)

        if not results:
            print("❌ No similar chunks found!")
            continue

        # Generate answer using LLM
        try:
            answer_data = generator.generate_answer(query, results)

            print(f"\n✅ Answer:")
            print(f"{answer_data.answer_text}")
            print(f"\n📎 Citations:")
            for citation in answer_data.citations:
                print(f"   • {citation.document_title} - {citation.section_path}")
                print(f"     (Relevance: {citation.relevance_score:.2%})")
            print(f"\nConfidence: {answer_data.confidence_level.value}")
            print(f"Cost: ${answer_data.cost_usd:.4f}")
            print(f"Time: {answer_data.generation_time_seconds:.2f}s")
        except Exception as e:
            print(f"❌ Error generating answer: {e}")


def main():
    """Main test function"""
    print("\n" + "="*80)
    print("RAG CHATBOT TESTING SCRIPT")
    print("="*80)

    # Parse arguments
    setup_type = "free"  # Default to FREE setup
    if len(sys.argv) > 1:
        if "--free" in sys.argv:
            setup_type = "free"
        elif "--hybrid" in sys.argv:
            setup_type = "hybrid"

    print(f"\n🔧 Setup: {setup_type.upper()}")

    # Step 1: Process documents
    chunks = test_document_processing()
    if not chunks:
        return

    # Step 2: Embed chunks
    if setup_type == "free":
        embedder = test_embedding_free(chunks)
        if embedder:
            test_queries_free(embedder)
    else:  # hybrid
        embedder = test_embedding_hybrid(chunks)
        if embedder:
            test_queries_hybrid(embedder)

    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review answers for accuracy")
    print("2. Check citations for correctness")
    print("3. Verify confidence scores")
    print("4. Add more policy documents to sample_data/")
    print("5. Fine-tune chunking or embedding as needed")


if __name__ == "__main__":
    main()
