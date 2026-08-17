"""
Document Chunking Module for RAG Knowledge Chatbot

This module provides multiple chunking strategies optimized for HR policy documents.
It includes semantic chunking, hierarchical chunking, and hybrid approaches to ensure
optimal retrieval and citation accuracy.

Author: RAG Development Team
Version: 1.0
Date: 2026-08-14
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import tiktoken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    text: str
    chunk_number: int
    section_path: str  # e.g., "2 > 2.1 > Eligibility"
    section_title: str
    start_offset: int  # Character position in original document
    end_offset: int
    token_count: int
    page_number: Optional[int] = None
    document_title: Optional[str] = None


class DocumentChunker:
    """
    Main chunking class supporting multiple strategies optimized for HR policies.

    Supported strategies:
    1. HIERARCHICAL_CHUNKING - Uses document structure (best for policies)
    2. SEMANTIC_CHUNKING - Groups by semantic similarity
    3. RECURSIVE_CHUNKING - Recursive character-level splitting
    4. HYBRID_CHUNKING - Combines hierarchical with size constraints
    """

    # Configuration constants
    DEFAULT_CHUNK_SIZE = 400  # tokens
    DEFAULT_OVERLAP = 75  # tokens
    MIN_CHUNK_SIZE = 50  # minimum tokens
    MAX_CHUNK_SIZE = 2000  # maximum tokens

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
        strategy: str = "HYBRID",
        encoding_model: str = "cl100k_base"
    ):
        """
        Initialize the DocumentChunker.

        Args:
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
            strategy: Chunking strategy to use
            encoding_model: Tokenizer encoding model
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy
        self.tokenizer = tiktoken.get_encoding(encoding_model)

        logger.info(f"DocumentChunker initialized with strategy: {strategy}")
        logger.info(f"Chunk size: {chunk_size} tokens, Overlap: {overlap} tokens")

    def chunk_document(
        self,
        text: str,
        document_title: str = "Untitled",
        document_structure: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        Chunk a document using the configured strategy.

        Args:
            text: Document text to chunk
            document_title: Title of the document
            document_structure: Optional structure metadata

        Returns:
            List of Chunk objects
        """
        if self.strategy == "HIERARCHICAL":
            return self._hierarchical_chunking(text, document_title, document_structure)
        elif self.strategy == "SEMANTIC":
            return self._semantic_chunking(text, document_title)
        elif self.strategy == "RECURSIVE":
            return self._recursive_chunking(text, document_title)
        elif self.strategy == "HYBRID":
            return self._hybrid_chunking(text, document_title, document_structure)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"Token counting error: {e}. Using word count estimate.")
            return len(text.split())

    def _hierarchical_chunking(
        self,
        text: str,
        document_title: str,
        document_structure: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        HIERARCHICAL CHUNKING (RECOMMENDED for HR policies)

        Strategy: Respects document structure (headings, sections, subsections)

        Why it's best for HR policies:
        1. Preserves semantic structure (sections stay together)
        2. Maintains context for citations (clear section paths)
        3. Respects logical boundaries in policy documents
        4. Easier to attribute answers to specific policy sections
        5. Better for regulatory compliance (clear section references)

        Implementation:
        - Identify heading levels (H1, H2, H3)
        - Split on major headings first (H1)
        - Further split on H2/H3 if needed for size
        - Respect section coherence

        Example:
        Policy: "Remote Work Policy"
        ├─ 1. Overview
        ├─ 2. Eligibility
        │  ├─ 2.1 Role Requirements
        │  └─ 2.2 Approval Process
        ├─ 3. Work Schedule
        └─ 4. Equipment & Technology

        Each section becomes a chunk with clear hierarchy path.
        """
        chunks = []
        chunk_number = 1

        # Extract sections using heading patterns (H1, H2, H3)
        # Pattern: # Heading (H1), ## Heading (H2), ### Heading (H3)
        h1_pattern = r'^# +(.+)$'
        h2_pattern = r'^## +(.+)$'
        h3_pattern = r'^### +(.+)$'

        lines = text.split('\n')
        current_h1 = "Introduction"
        current_h2 = ""
        current_h3 = ""
        current_section_text = []
        current_offset = 0

        for i, line in enumerate(lines):
            # Check heading levels
            h1_match = re.match(h1_pattern, line)
            h2_match = re.match(h2_pattern, line)
            h3_match = re.match(h3_pattern, line)

            if h1_match:
                # Save previous section if exists
                if current_section_text:
                    section_text = '\n'.join(current_section_text)
                    if self._count_tokens(section_text) >= self.MIN_CHUNK_SIZE:
                        chunk = self._create_chunk(
                            text=section_text,
                            chunk_number=chunk_number,
                            section_path=f"{current_h1} > {current_h2} > {current_h3}".replace(" > ", ">", -3),
                            section_title=current_h3 or current_h2 or current_h1,
                            start_offset=current_offset,
                            document_title=document_title
                        )
                        chunks.append(chunk)
                        chunk_number += 1
                        current_offset = sum(len(l) + 1 for l in current_section_text)

                current_h1 = h1_match.group(1)
                current_h2 = ""
                current_h3 = ""
                current_section_text = [line]

            elif h2_match:
                # Save previous H2 section if large enough
                if current_section_text and self._count_tokens('\n'.join(current_section_text)) > self.chunk_size:
                    section_text = '\n'.join(current_section_text)
                    chunk = self._create_chunk(
                        text=section_text,
                        chunk_number=chunk_number,
                        section_path=f"{current_h1} > {current_h2}",
                        section_title=current_h2,
                        start_offset=current_offset,
                        document_title=document_title
                    )
                    chunks.append(chunk)
                    chunk_number += 1
                    current_offset += len(section_text)
                    current_section_text = []

                current_h2 = h2_match.group(1)
                current_h3 = ""
                current_section_text.append(line)

            elif h3_match:
                current_h3 = h3_match.group(1)
                current_section_text.append(line)

            else:
                current_section_text.append(line)

        # Add final section
        if current_section_text:
            section_text = '\n'.join(current_section_text)
            if self._count_tokens(section_text) >= self.MIN_CHUNK_SIZE:
                chunk = self._create_chunk(
                    text=section_text,
                    chunk_number=chunk_number,
                    section_path=f"{current_h1} > {current_h2} > {current_h3}".replace(" > ", ">", -3),
                    section_title=current_h3 or current_h2 or current_h1,
                    start_offset=current_offset,
                    document_title=document_title
                )
                chunks.append(chunk)

        logger.info(f"Hierarchical chunking created {len(chunks)} chunks")
        return chunks

    def _semantic_chunking(self, text: str, document_title: str) -> List[Chunk]:
        """
        SEMANTIC CHUNKING

        Strategy: Groups text by semantic boundaries (sentences, paragraphs)

        Why it's useful:
        1. Preserves sentence integrity
        2. Better semantic coherence than random splits
        3. Good for flowing text without clear structure
        4. Respects natural language boundaries

        Less ideal for HR policies because:
        - Loses structural information
        - Harder to cite specific policy sections
        - Less precise for regulation-focused queries

        Implementation:
        - Split by sentences first
        - Group sentences until chunk size reached
        - Add overlap between chunks
        """
        chunks = []
        chunk_number = 1

        # Split into sentences (roughly)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk_tokens = 0
        current_chunk_text = []
        current_offset = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If adding sentence exceeds limit, save current chunk
            if current_chunk_tokens + sentence_tokens > self.chunk_size and current_chunk_text:
                chunk_text = ' '.join(current_chunk_text)
                chunk = self._create_chunk(
                    text=chunk_text,
                    chunk_number=chunk_number,
                    section_path="Body Text",
                    section_title="Body Text",
                    start_offset=current_offset,
                    document_title=document_title
                )
                chunks.append(chunk)
                chunk_number += 1

                # Add overlap
                current_chunk_text = current_chunk_text[-2:] if len(current_chunk_text) > 2 else current_chunk_text
                current_chunk_tokens = sum(self._count_tokens(s) for s in current_chunk_text)
                current_offset += len(chunk_text)

            current_chunk_text.append(sentence)
            current_chunk_tokens += sentence_tokens

        # Add final chunk
        if current_chunk_text:
            chunk_text = ' '.join(current_chunk_text)
            chunk = self._create_chunk(
                text=chunk_text,
                chunk_number=chunk_number,
                section_path="Body Text",
                section_title="Body Text",
                start_offset=current_offset,
                document_title=document_title
            )
            chunks.append(chunk)

        logger.info(f"Semantic chunking created {len(chunks)} chunks")
        return chunks

    def _recursive_chunking(self, text: str, document_title: str) -> List[Chunk]:
        """
        RECURSIVE CHARACTER CHUNKING

        Strategy: Recursively splits text on delimiters (paragraphs, sentences, words)

        Why it's useful:
        1. Handles documents with varying structure
        2. Guarantees chunk size limits
        3. Works with unstructured text
        4. Flexible delimiter hierarchy

        Less ideal for HR policies because:
        - Can split in middle of important sections
        - Loses semantic structure
        - May separate related content

        Implementation:
        - Try split on '\n\n' (paragraphs)
        - If too large, split on '\n' (lines)
        - If still too large, split on '. ' (sentences)
        - If still too large, split on ' ' (words)
        """
        chunks = []
        chunk_number = 1
        delimiters = ['\n\n', '\n', '. ', ' ']

        def recursive_split(text_to_split: str, delimiter_idx: int = 0) -> List[str]:
            """Recursively split text on delimiters."""
            if delimiter_idx >= len(delimiters):
                # Last resort: split by character
                return [text_to_split[i:i+self.chunk_size]
                       for i in range(0, len(text_to_split), self.chunk_size)]

            delimiter = delimiters[delimiter_idx]
            if delimiter not in text_to_split:
                return recursive_split(text_to_split, delimiter_idx + 1)

            splits = text_to_split.split(delimiter)

            # Group splits by size
            good_splits = []
            current = ""

            for split in splits:
                if self._count_tokens(current + delimiter + split) < self.chunk_size:
                    current += delimiter + split if current else split
                else:
                    if current:
                        good_splits.append(current)
                    if self._count_tokens(split) < self.chunk_size:
                        current = split
                    else:
                        good_splits.extend(recursive_split(split, delimiter_idx + 1))
                        current = ""

            if current:
                good_splits.append(current)

            return good_splits

        text_chunks = recursive_split(text)
        current_offset = 0

        for chunk_text in text_chunks:
            if self._count_tokens(chunk_text) >= self.MIN_CHUNK_SIZE:
                chunk = self._create_chunk(
                    text=chunk_text,
                    chunk_number=chunk_number,
                    section_path="Body Text",
                    section_title="Body Text",
                    start_offset=current_offset,
                    document_title=document_title
                )
                chunks.append(chunk)
                chunk_number += 1
                current_offset += len(chunk_text)

        logger.info(f"Recursive chunking created {len(chunks)} chunks")
        return chunks

    def _hybrid_chunking(
        self,
        text: str,
        document_title: str,
        document_structure: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        HYBRID CHUNKING (RECOMMENDED FOR HR POLICIES)

        Strategy: Combines hierarchical chunking with size constraints

        Why it's BEST for HR policy documents:

        1. PRESERVES STRUCTURE
           - Respects document headings and sections
           - Maintains policy hierarchy
           - Clear section paths for citations

        2. RESPECTS SIZE CONSTRAINTS
           - Enforces token limits (300-500 tokens)
           - Prevents overly large or small chunks
           - Optimal for embedding models

        3. MAINTAINS CONTEXT
           - Overlapping chunks for context
           - Related information stays together
           - Better for multi-turn conversations

        4. CITATION ACCURACY
           - Clear document path: "Remote Work Policy > 2. Eligibility > 2.1 Approval"
           - Easy to attribute answers to source sections
           - Regulatory compliance ready

        5. RETRIEVAL QUALITY
           - Semantic coherence within chunks
           - Reduced ambiguity in meaning
           - Better embedding quality

        Implementation:
        - First pass: Use hierarchical structure
        - Second pass: Refine chunks by size
        - Add overlap for context preservation
        - Create proper section paths

        Example Output:
        Chunk 1: "Remote Work Policy > 1. Overview"
                 Text: "This policy outlines... [400 tokens]"
                 Path: "1"
                 Overlap: Previous 75 tokens

        Chunk 2: "Remote Work Policy > 2. Eligibility"
                 Text: "All employees are eligible... [450 tokens]"
                 Path: "2"
                 Overlap: Last 75 tokens from Chunk 1
        """
        chunks = []
        chunk_number = 1

        # Step 1: Extract sections with headers
        sections = self._extract_sections(text)

        # Step 2: Process each section, respecting size constraints
        for section in sections:
            section_text = section['text']
            section_title = section['title']
            section_number = section['number']
            current_offset = section['offset']

            # If section fits in one chunk, use it as-is
            if self._count_tokens(section_text) <= self.chunk_size:
                chunk = self._create_chunk(
                    text=section_text,
                    chunk_number=chunk_number,
                    section_path=section_number,
                    section_title=section_title,
                    start_offset=current_offset,
                    document_title=document_title
                )
                chunks.append(chunk)
                chunk_number += 1
            else:
                # Split large section further
                sub_chunks = self._split_large_section(
                    section_text,
                    section_number,
                    section_title,
                    current_offset
                )
                for sub_chunk_text, sub_offset, sub_path in sub_chunks:
                    chunk = self._create_chunk(
                        text=sub_chunk_text,
                        chunk_number=chunk_number,
                        section_path=sub_path,
                        section_title=section_title,
                        start_offset=sub_offset,
                        document_title=document_title
                    )
                    chunks.append(chunk)
                    chunk_number += 1

        # Step 3: Add overlap between chunks
        chunks = self._add_overlap(chunks, text)

        logger.info(f"Hybrid chunking created {len(chunks)} chunks from {len(sections)} sections")
        return chunks

    def _extract_sections(self, text: str) -> List[Dict]:
        """Extract sections from text based on heading patterns."""
        sections = []
        lines = text.split('\n')

        current_section = None
        current_text = []
        current_offset = 0

        h1_pattern = r'^#{1,3} +(.+)$'

        for line in lines:
            match = re.match(h1_pattern, line)

            if match:
                # Save previous section
                if current_section and current_text:
                    current_section['text'] = '\n'.join(current_text)
                    sections.append(current_section)
                    current_offset += len(current_section['text'])

                # Start new section
                heading_level = len(match.group(0)) - len(match.group(0).lstrip('#'))
                title = match.group(1)

                current_section = {
                    'title': title,
                    'number': title.split()[0] if title.split()[0][0].isdigit() else title,
                    'level': heading_level,
                    'offset': current_offset
                }
                current_text = [line]
            else:
                if current_section:
                    current_text.append(line)

        # Add final section
        if current_section and current_text:
            current_section['text'] = '\n'.join(current_text)
            sections.append(current_section)

        return sections

    def _split_large_section(
        self,
        text: str,
        section_number: str,
        section_title: str,
        offset: int
    ) -> List[Tuple[str, int, str]]:
        """Split a large section into smaller chunks."""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = []
        current_tokens = 0
        current_offset = offset
        sub_chunk_num = 1

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk_path = f"{section_number}.{sub_chunk_num}"
                chunks.append((chunk_text, current_offset, chunk_path))

                current_offset += len(chunk_text)
                current_chunk = [sentence]
                current_tokens = sentence_tokens
                sub_chunk_num += 1
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_path = f"{section_number}.{sub_chunk_num}"
            chunks.append((chunk_text, current_offset, chunk_path))

        return chunks

    def _add_overlap(self, chunks: List[Chunk], original_text: str) -> List[Chunk]:
        """Add overlapping context between chunks."""
        if len(chunks) <= 1:
            return chunks

        # Calculate overlap in characters based on token overlap
        overlap_char_estimate = int((self.overlap / self.chunk_size) * 200)  # rough estimate

        updated_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Add previous chunk's end as overlap context
                prev_chunk = chunks[i - 1]
                overlap_text = prev_chunk.text[-overlap_char_estimate:]
                chunk.text = overlap_text + '\n...\n' + chunk.text

            updated_chunks.append(chunk)

        return updated_chunks

    def _create_chunk(
        self,
        text: str,
        chunk_number: int,
        section_path: str,
        section_title: str,
        start_offset: int,
        document_title: str = ""
    ) -> Chunk:
        """Create a Chunk object with all metadata."""
        token_count = self._count_tokens(text)

        return Chunk(
            text=text,
            chunk_number=chunk_number,
            section_path=section_path,
            section_title=section_title,
            start_offset=start_offset,
            end_offset=start_offset + len(text),
            token_count=token_count,
            document_title=document_title
        )


def demonstrate_chunking_strategies():
    """
    Demonstrate different chunking strategies on sample HR policy.
    """

    sample_policy = """
# Remote Work Policy

## 1. Overview

This policy establishes guidelines for remote work arrangements at our organization.
The remote work program is designed to provide flexibility while ensuring business continuity,
employee productivity, and effective collaboration.

Remote work is defined as performing job duties from locations other than the primary office,
including home, satellite offices, or approved alternative work locations.

## 2. Eligibility

### 2.1 Role Requirements

Not all positions are suitable for remote work. Eligibility depends on the nature of job duties.

Eligible roles typically include:
- Positions that primarily involve computer-based work
- Roles with limited in-person interaction requirements
- Jobs that don't require specialized equipment on-site
- Positions where performance can be measured by output rather than presence

Ineligible roles include:
- Positions requiring hands-on equipment interaction
- Client-facing roles requiring physical presence
- Positions requiring classified information handling in secure facilities

### 2.2 Approval Process

1. Employee submits request to manager with justification
2. Manager evaluates role suitability and individual performance
3. HR reviews request for compliance and precedent
4. Final approval by department head required
5. Remote work agreement signed before commencement

Approval does not guarantee permanent remote work status. The arrangement remains subject to
business needs and performance expectations.

## 3. Work Schedule

### 3.1 Core Hours

All remote employees must be available during core business hours (9 AM - 5 PM local time).

Core hours include:
- Attendance at required team meetings
- Responsiveness to messages and emails
- Availability for critical business situations

### 3.2 Remote Work Types

**Full-Time Remote:** 5 days per week
- Requires quarterly office visits for team collaboration
- Occasional in-person meetings as needed
- Annual team offsite attendance required

**Hybrid Remote:** 2-3 days per week in office
- Remaining days flexible for remote work
- Schedule coordinated with team
- No additional office day requirement

**Flexible Remote:** Ad-hoc basis
- Advance notice required (minimum 24 hours)
- Cannot exceed 2 days per week
- Subject to manager approval

## 4. Equipment and Technology

### 4.1 Equipment Provision

The company provides:
- Laptop or desktop computer (as appropriate for role)
- Monitor and peripheral devices
- VPN access and security software
- Collaboration tools and software licenses

### 4.2 Internet Requirements

Employees must provide reliable internet connectivity:
- Minimum 25 Mbps download speed
- Minimum 5 Mbps upload speed
- Stable connection without frequent interruptions

The company does not reimburse internet costs. However, internet-dependent remote workers may
be eligible for equipment allowances.

### 4.3 Cybersecurity Requirements

All remote work must comply with cybersecurity policies:
- VPN required for all company system access
- Multi-factor authentication enabled
- Regular security updates and patches
- No public WiFi for company work
- Secure home office setup maintaining confidentiality
"""

    print("\n" + "="*80)
    print("DOCUMENT CHUNKING STRATEGIES DEMONSTRATION")
    print("="*80 + "\n")

    # Demonstrate HYBRID chunking (recommended)
    print("1️⃣  HYBRID CHUNKING (RECOMMENDED FOR HR POLICIES)")
    print("-" * 80)

    chunker = DocumentChunker(strategy="HYBRID", chunk_size=400, overlap=75)
    chunks = chunker.chunk_document(sample_policy, "Remote Work Policy")

    print(f"Total chunks created: {len(chunks)}\n")

    for chunk in chunks[:3]:  # Show first 3 chunks
        print(f"Chunk {chunk.chunk_number}:")
        print(f"  Section Path: {chunk.section_path}")
        print(f"  Title: {chunk.section_title}")
        print(f"  Tokens: {chunk.token_count}")
        print(f"  Text preview: {chunk.text[:150]}...")
        print()

    # Demonstrate HIERARCHICAL chunking
    print("\n2️⃣  HIERARCHICAL CHUNKING")
    print("-" * 80)

    chunker_hier = DocumentChunker(strategy="HIERARCHICAL", chunk_size=400, overlap=75)
    chunks_hier = chunker_hier.chunk_document(sample_policy, "Remote Work Policy")

    print(f"Total chunks created: {len(chunks_hier)}\n")
    print("Section paths created:")
    for chunk in chunks_hier:
        print(f"  - {chunk.section_path}: {chunk.token_count} tokens")

    # Demonstrate SEMANTIC chunking
    print("\n3️⃣  SEMANTIC CHUNKING")
    print("-" * 80)

    chunker_sem = DocumentChunker(strategy="SEMANTIC", chunk_size=400, overlap=75)
    chunks_sem = chunker_sem.chunk_document(sample_policy, "Remote Work Policy")

    print(f"Total chunks created: {len(chunks_sem)}\n")
    print(f"Average chunk size: {sum(c.token_count for c in chunks_sem) // len(chunks_sem)} tokens")

    # Print comparison
    print("\n" + "="*80)
    print("CHUNKING STRATEGY COMPARISON")
    print("="*80 + "\n")

    comparison_data = [
        ["Strategy", "Chunks Created", "Best For", "Structure Preservation"],
        ["Hybrid", len(chunks), "HR Policies ⭐", "Excellent"],
        ["Hierarchical", len(chunks_hier), "Structured Docs", "Perfect"],
        ["Semantic", len(chunks_sem), "Narrative Text", "Good"],
    ]

    for row in comparison_data:
        print(f"{row[0]:20} {row[1]:15} {row[2]:20} {row[3]:20}")

    print("\n" + "="*80)
    print("WHY HYBRID CHUNKING IS BEST FOR HR POLICIES")
    print("="*80 + "\n")

    reasons = [
        ("1. Structure Preservation",
         "Respects heading hierarchy (1. Overview > 2. Eligibility > 2.1 Approval)\n"
         "   Makes it easy to cite 'Section 2.1 Approval Process'"),

        ("2. Citation Accuracy",
         "Clear section paths enable precise source attribution\n"
         "   User: 'How do I get remote work approved?'\n"
         "   Answer cites: Remote Work Policy > 2.2 Approval Process"),

        ("3. Optimal Chunk Size",
         "Enforces 300-500 token limit (perfect for embeddings)\n"
         "   Not too small (< 50 tokens = lost context)\n"
         "   Not too large (> 2000 tokens = poor relevance)"),

        ("4. Context Preservation",
         "Overlapping chunks (75 tokens) maintain context\n"
         "   Reader understands full policy intent from one chunk"),

        ("5. Regulatory Compliance",
         "Policy sections map directly to compliance requirements\n"
         "   Auditors can verify policy adherence by section"),

        ("6. Conversation Quality",
         "Multi-turn conversations stay coherent\n"
         "   Follow-up questions find related sections naturally"),
    ]

    for title, explanation in reasons:
        print(f"\n{title}")
        print(f"  {explanation}")


if __name__ == "__main__":
    """Run demonstration of chunking strategies."""
    demonstrate_chunking_strategies()

    print("\n" + "="*80)
    print("USAGE EXAMPLE")
    print("="*80 + "\n")

    usage_code = '''
from document_chunking import DocumentChunker, Chunk

# Initialize chunker with HYBRID strategy (recommended)
chunker = DocumentChunker(
    chunk_size=400,      # tokens
    overlap=75,          # tokens
    strategy="HYBRID"    # best for HR policies
)

# Chunk your document
with open("remote_work_policy.pdf") as f:
    policy_text = f.read()

chunks = chunker.chunk_document(
    text=policy_text,
    document_title="Remote Work Policy"
)

# Use chunks for embedding and indexing
for chunk in chunks:
    print(f"Section: {chunk.section_path}")
    print(f"Tokens: {chunk.token_count}")

    # Send to embedding API
    embedding = embedding_model.embed(chunk.text)

    # Store in vector DB with metadata
    vector_db.insert(
        id=chunk.id,
        vector=embedding,
        metadata={
            "section": chunk.section_path,
            "title": chunk.section_title,
            "document": chunk.document_title
        }
    )
'''

    print(usage_code)
