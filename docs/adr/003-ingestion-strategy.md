# ADR-003: Ingestion Strategy and Chunking

## Status
Accepted

## Context
High-quality retrieval depends on how documents are parsed and split. We need to maintain context and allow for precise citations (page numbers).

## Decision
1. Use `PyPDFLoader` for initial parsing.
2. Use `RecursiveCharacterTextSplitter` with chunk_size=1000 and chunk_overlap=200.
3. Metadata MUST include: `source_file`, `page_number`, and `chunk_id`.
4. Apply PII masking BEFORE embedding to ensure sensitive data is not stored in the vector space.

## Rationale
- **Precise Citations**: By storing page numbers in metadata, the system can reliably attribute answers to specific parts of the source document.
- **Context Retention**: `RecursiveCharacterTextSplitter` is chosen for its ability to split text along logical boundaries (paragraphs, sentences), preserving semantic coherence better than simple character counting.
- **Privacy by Design**: Masking PII before embedding prevents sensitive information from being leaked into the vector database, aligning with GDPR requirements.

## Consequences
- **Pros**: Accurate source attribution, GDPR compliance at rest, balanced semantic meaning.
- **Cons**: Slightly higher processing time per document due to the masking and logical splitting steps.
