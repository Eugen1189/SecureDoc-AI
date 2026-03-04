# ADR-005: Testing and Validation Strategy

## Status
Accepted

## Context
In a RAG system, we must ensure that:
1. PII masking logic doesn't break.
2. The retrieval service correctly interfaces with Qdrant.
3. The API contract remains stable.

## Decision
1. Implement **Unit Tests** for `pii_masker` and `pdf_service`.
2. Implement **Integration Tests** using a mocked Qdrant client to verify retrieval logic without an active DB connection.
3. Use `pytest-asyncio` for asynchronous endpoint testing.

## Rationale
- **Reliability**: Automated tests ensure that security-critical features (PII masking) work as expected and don't regress over time.
- **Portability**: Mocking external services (OpenAI, Qdrant) allows tests to run in CI environments without needing live API keys or database instances.
- **Contract Safety**: API tests guarantee that changes to the backend don't break the communication with potential frontend clients.

## Consequences
- **Pros**: Prevents regressions, allows for safe refactoring, and ensures compliance with security rules.
- **Cons**: Requires maintenance of mocks for OpenAI and Qdrant APIs as their interfaces evolve.
