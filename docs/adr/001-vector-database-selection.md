# ADR-001: Vector Database Selection

## Status
Accepted

## Context
The project requires a vector database to store document embeddings for Retrieval-Augmented Generation (RAG). To meet enterprise-grade requirements, the database must support complex metadata (payload) and allow for efficient filtering directly at the database level.

## Decision
We have chosen **Qdrant** as our vector database.

## Rationale
- **Payload Support**: Qdrant allows storing complex metadata alongside vectors, which is essential for managing document context and permissions.
- **Filtering**: It supports advanced filtering on metadata fields during the search process, reducing the need for post-filtering and improving performance.
- **Enterprise Ready**: Qdrant is built for performance and scalability, making it suitable for enterprise applications.

## Consequences
- **Positive**: High search efficiency and flexibility in data modeling.
- **Negative**: Requires setup and maintenance of Qdrant (either via Docker, Cloud, or custom deployment).
