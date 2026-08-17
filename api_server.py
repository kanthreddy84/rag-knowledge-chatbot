"""
FastAPI server for DataFactZ HR Policy Assistant RAG Chatbot
Connects the React web app to the RAG backend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

# Import RAG modules
from improved_chunking import ImprovedChunker
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI(
    title="DataFactZ RAG API",
    description="Backend API for HR Policy Assistant",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    chunker = ImprovedChunker(chunk_size=300, overlap=50)
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")

# In-memory storage (replace with database for production)
documents_store = []
chunks_store = []
embeddings_store = []
full_documents = {}  # Store full document text for viewing

# Pydantic models
class Citation(BaseModel):
    document_title: str
    document_id: str  # Actual document ID for API calls
    section_path: str
    excerpt: str
    relevance_score: float
    chunk_index: Optional[int] = None  # Index for retrieving full context

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: str
    generation_time_seconds: float

class DocumentInfo(BaseModel):
    id: str
    filename: str
    title: str
    description: str
    chunk_count: int
    token_count: int
    indexed_at: str
    status: str

class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]

# Routes

@app.get("/health")
async def health_check():
    """Check API health"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True,
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Process a natural language query against indexed documents

    Returns grounded answer with citations
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if not chunks_store or not embeddings_store:
        raise HTTPException(
            status_code=503,
            detail="No documents indexed. Please index documents first."
        )

    try:
        import time
        start_time = time.time()

        # Embed query
        query_embedding = embedding_model.encode(request.query, show_progress_bar=False)

        # Find similar chunks
        similarities = cosine_similarity([query_embedding], embeddings_store)[0]
        top_indices = np.argsort(similarities)[::-1][:5]

        # Extract citations (lower threshold for better matching)
        citations = []
        for idx in top_indices:
            if similarities[idx] > 0.2:  # Lowered threshold
                chunk = chunks_store[idx]
                # Get more context from the chunk
                excerpt = chunk['text'][:300] if len(chunk['text']) > 300 else chunk['text']

                # Get document_id from documents_store
                doc_title = chunk.get('document_title', 'Unknown')
                doc_id = next((d.id for d in documents_store if d.title == doc_title.replace('_', ' ').title()), doc_title)

                citations.append(Citation(
                    document_title=doc_title,
                    document_id=doc_id,
                    section_path=chunk.get('section_path', ''),
                    excerpt=excerpt,
                    relevance_score=float(similarities[idx]),
                    chunk_index=idx
                ))

        # Determine confidence level (adjusted for lower scores)
        if len(citations) > 0:
            top_score = citations[0].relevance_score
            if top_score > 0.5:
                confidence = "HIGH"
            elif top_score > 0.3:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            confidence = "LOW"

        # Build answer with bullet point formatting
        if citations:
            # Format each citation as a section
            formatted_sections = []
            for i, c in enumerate(citations[:3], 1):
                # Extract key points from excerpt
                excerpt_lines = c.excerpt.strip().split('\n')
                points = [line.strip() for line in excerpt_lines if line.strip() and len(line.strip()) > 10]

                section = f"## {i}️⃣ **{c.document_title}**\n\n**Section:** {c.section_path}\n\n**Key Points:**\n"
                for point in points[:5]:  # Limit to 5 points per section
                    section += f"• {point}\n"
                section += f"\n**Match Score:** {int(c.relevance_score * 100)}%"
                formatted_sections.append(section)

            answer = "## 📋 **ANSWER**\n\n" + "\n\n---\n\n".join(formatted_sections)
        else:
            answer = "❌ I couldn't find relevant information in the policy documents.\n\n**Try:** Rephrase your question or ask about specific topics like vacation, remote work, or conduct."

        generation_time = time.time() - start_time

        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            generation_time_seconds=generation_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.get("/api/documents", response_model=DocumentsResponse)
async def get_documents():
    """Get list of indexed documents"""
    return DocumentsResponse(documents=documents_store)

@app.post("/api/reindex")
async def reindex_documents():
    """Reindex all documents in sample_data folder"""
    global chunks_store, embeddings_store, documents_store, full_documents

    try:
        data_folder = Path("sample_data")

        if not data_folder.exists():
            raise HTTPException(status_code=400, detail="sample_data folder not found")

        policy_files = list(data_folder.glob("*.txt"))

        if not policy_files:
            raise HTTPException(status_code=400, detail="No text files found in sample_data")

        # Reset stores
        chunks_store = []
        embeddings_store = []
        documents_store = []
        full_documents = {}

        # Process each document
        for file_path in sorted(policy_files):
            # Read full document text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_text = f.read()
            full_documents[file_path.stem] = full_text

            # Use improved chunker
            chunks = chunker.process_document(file_path, file_path.stem)

            # Store chunks
            for chunk_dict in chunks:
                chunks_store.append(chunk_dict)

            # Create embeddings
            chunk_texts = [c['text'] for c in chunks]
            chunk_embeddings = embedding_model.encode(chunk_texts, show_progress_bar=False)
            embeddings_store.extend(chunk_embeddings)

            # Add document info
            total_tokens = sum(c['token_count'] for c in chunks)
            documents_store.append(DocumentInfo(
                id=file_path.stem,
                filename=file_path.name,
                title=file_path.stem.replace('_', ' ').title(),
                description=f"HR policy document with {len(chunks)} chunks",
                chunk_count=len(chunks),
                token_count=total_tokens,
                indexed_at=datetime.now().isoformat(),
                status="indexed"
            ))

        return {
            "status": "success",
            "documents_indexed": len(documents_store),
            "total_chunks": len(chunks_store),
            "total_tokens": sum(d.token_count for d in documents_store)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex error: {str(e)}")

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    global documents_store

    documents_store = [d for d in documents_store if d.id != doc_id]
    return {"status": "deleted", "document_id": doc_id}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a new document"""
    try:
        # Save file
        save_path = Path("sample_data") / file.filename
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process document
        with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        chunks = chunker.chunk_document(text, document_title=save_path.stem)

        # Store chunks and embeddings
        for chunk in chunks:
            chunks_store.append({
                'text': chunk.text,
                'document_title': chunk.document_title,
                'section_path': chunk.section_path,
                'chunk_number': chunk.chunk_number,
                'token_count': chunk.token_count,
            })

        chunk_texts = [c.text for c in chunks]
        chunk_embeddings = embedding_model.encode(chunk_texts, show_progress_bar=False)
        embeddings_store.extend(chunk_embeddings)

        # Add document info
        total_tokens = sum(c.token_count for c in chunks)
        doc_info = DocumentInfo(
            id=save_path.stem,
            filename=file.filename,
            title=save_path.stem.replace('_', ' ').title(),
            description="Newly uploaded document",
            chunk_count=len(chunks),
            token_count=total_tokens,
            indexed_at=datetime.now().isoformat(),
            status="indexed"
        )
        documents_store.append(doc_info)

        return {
            "status": "uploaded",
            "filename": file.filename,
            "chunks": len(chunks),
            "tokens": total_tokens
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.get("/api/documents/{doc_id}/content")
async def get_document_content(doc_id: str):
    """Retrieve full document text for viewing"""
    if doc_id not in full_documents:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

    return {
        "document_id": doc_id,
        "content": full_documents[doc_id],
        "title": doc_id.replace('_', ' ').title()
    }

@app.get("/api/chunks/{chunk_index}")
async def get_chunk_context(chunk_index: int):
    """Retrieve a specific chunk with surrounding context"""
    if chunk_index < 0 or chunk_index >= len(chunks_store):
        raise HTTPException(status_code=404, detail="Chunk not found")

    chunk = chunks_store[chunk_index]

    # Get surrounding chunks for context
    context_before = chunks_store[chunk_index - 1]['text'] if chunk_index > 0 else ""
    context_after = chunks_store[chunk_index + 1]['text'] if chunk_index < len(chunks_store) - 1 else ""

    return {
        "chunk_index": chunk_index,
        "document_title": chunk.get('document_title', 'Unknown'),
        "section_path": chunk.get('section_path', ''),
        "text": chunk['text'],
        "context_before": context_before,
        "context_after": context_after,
        "chunk_number": chunk.get('chunk_number', 0),
        "token_count": chunk.get('token_count', 0)
    }

@app.get("/docs", include_in_schema=True)
async def get_docs():
    """API documentation"""
    return {
        "title": "DataFactZ RAG API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - Check API health",
            "POST /api/query - Query documents",
            "GET /api/documents - List indexed documents",
            "GET /api/documents/{doc_id}/content - Get full document",
            "GET /api/chunks/{chunk_index} - Get specific chunk",
            "POST /api/reindex - Reindex all documents",
            "DELETE /api/documents/{doc_id} - Delete document",
            "POST /api/documents/upload - Upload new document",
        ]
    }

@app.on_event("startup")
async def startup_event():
    """Auto-reindex documents on startup"""
    global chunks_store, embeddings_store, documents_store, full_documents

    try:
        data_folder = Path("sample_data")
        if data_folder.exists():
            policy_files = list(data_folder.glob("*.txt"))
            if policy_files:
                print("Indexing sample documents on startup...")
                chunks_store = []
                embeddings_store = []
                documents_store = []
                full_documents = {}

                for file_path in sorted(policy_files):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        full_text = f.read()
                    full_documents[file_path.stem] = full_text

                    chunks = chunker.process_document(file_path, file_path.stem)
                    for chunk_dict in chunks:
                        chunks_store.append(chunk_dict)

                    chunk_texts = [c['text'] for c in chunks]
                    chunk_embeddings = embedding_model.encode(chunk_texts, show_progress_bar=False)
                    embeddings_store.extend(chunk_embeddings)

                    total_tokens = sum(c['token_count'] for c in chunks)
                    documents_store.append(DocumentInfo(
                        id=file_path.stem,
                        filename=file_path.name,
                        title=file_path.stem.replace('_', ' ').title(),
                        description=f"HR policy document with {len(chunks)} chunks",
                        chunk_count=len(chunks),
                        token_count=total_tokens,
                        indexed_at=datetime.now().isoformat(),
                        status="indexed"
                    ))

                print(f"✓ Indexed {len(documents_store)} documents with {len(chunks_store)} chunks")
    except Exception as e:
        print(f"Error during startup indexing: {e}")

if __name__ == "__main__":
    import uvicorn
    print("Starting DataFactZ RAG API Server...")
    print("Available at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
