"""
Improved document chunking with section detection
Splits documents into smaller, semantically meaningful chunks
"""

import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
import tiktoken

class ImprovedChunker:
    def __init__(self, chunk_size=300, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def detect_sections(self, text):
        """Detect section headers and split document"""
        # Split by section numbers (1., 2., 2.1, etc.)
        section_pattern = r'(?=\n\d+\.|\n\d+\.\d+\.)'
        sections = re.split(section_pattern, text)

        chunks = []
        for section in sections:
            if len(section.strip()) < 50:
                continue

            # Split large sections by token count
            section_chunks = self._chunk_by_tokens(section)
            chunks.extend(section_chunks)

        return chunks

    def _chunk_by_tokens(self, text):
        """Split text into chunks by token count"""
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) > 1 else current_chunk[0]
                current_chunk = [overlap_text, sentence]
                current_tokens = self.count_tokens(overlap_text) + sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def process_document(self, file_path, doc_title):
        """Process entire document"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        chunks = self.detect_sections(text)

        result = []
        for idx, chunk_text in enumerate(chunks, 1):
            token_count = self.count_tokens(chunk_text)
            result.append({
                'text': chunk_text,
                'chunk_number': idx,
                'document_title': doc_title,
                'section_path': f'Section {idx}',
                'token_count': token_count,
            })

        return result


# Test the improved chunker
if __name__ == "__main__":
    chunker = ImprovedChunker(chunk_size=300, overlap=50)

    # Test on dress code document
    file_path = Path("sample_data/Code_of_Conduct.txt")
    chunks = chunker.process_document(file_path, "Code_of_Conduct")

    print(f"Document: {file_path.name}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Total tokens: {sum(c['token_count'] for c in chunks)}")
    print("\nChunks:")

    for i, chunk in enumerate(chunks[:10], 1):
        preview = chunk['text'][:100].replace('\n', ' ')
        print(f"\n{i}. Tokens: {chunk['token_count']}")
        print(f"   Preview: {preview}...")

        # Find dress code section
        if 'dress' in chunk['text'].lower():
            print("   ✓ CONTAINS DRESS CODE!")
