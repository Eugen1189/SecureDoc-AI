# ADR-004: Retrieval Strategy and Grounded Generation

## Status
Accepted

## Context
Users need answers that are strictly based on provided documents to avoid hallucinations. Each claim must be backed by a source reference.

## Decision
1. Use **Similarity Search** with a score threshold to ensure relevance.
2. Implement **Context Stuffing**: retrieval results (top-k) are injected into the LLM prompt.
3. Prompt Engineering: Instruct the LLM to use a specific format for citations, e.g., `[Source: filename, Page: X]`.
4. If no relevant information is found, the LLM must state that it cannot answer based on the provided documents.

## Rationale
- **Trustworthiness**: Mandatory citations allow users to verify the information against the original document.
- **Hallucination Mitigation**: By forcing the LLM to stay within the provided context and admitting when info is missing, we significantly reduce the risk of incorrect answers.
- **Relevance**: A score threshold prevents the model from trying to answer based on loosely related or irrelevant chunks.

## Consequences
- **Pros**: High factual accuracy, user trust via verification, minimal hallucinations.
- **Cons**: Answers are limited by the quality of the ingested chunks.
