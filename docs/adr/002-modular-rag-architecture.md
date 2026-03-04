# ADR-002: Modular RAG Architecture

## Status
Accepted

## Context
A monolithic approach to RAG (Retrieval-Augmented Generation) can lead to scaling bottlenecks. Document processing (ingestion) and query handling (retrieval) have different resource requirements and scaling patterns.

## Decision
We will adopt a **Modular RAG Architecture** that strictly separates the **Ingestion** and **Retrieval** processes.

## Rationale
- **Scalability**: Allows scaling the ingestion pipeline (e.g., during bulk uploads) independently from the retrieval service (e.g., during high user traffic).
- **Maintainability**: Each module can be developed, tested, and deployed independently.
- **Flexibility**: We can swap out components in the ingestion workflow (e.g., different parsers) or the retrieval workflow (e.g., different rerankers) without affecting the other.

## Consequences
- **Positive**: Clear separation of concerns and easier horizontal scaling.
- **Negative**: Adds some complexity to the initial system design and requires well-defined interfaces between modules.
