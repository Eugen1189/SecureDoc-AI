import os
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from unittest.mock import MagicMock, patch, AsyncMock
from src.api.main import app
from src.services.qdrant_service import VectorStoreService

client = TestClient(app)

@pytest.fixture
def sample_pdf_with_pii():
    file_path = "test_pii_document.pdf"
    c = canvas.Canvas(file_path)
    # Adding sensitive PII data
    pii_content = "Confidential Info: Email is john.doe@example.com, IBAN is DE89370400440532013000."
    c.drawString(100, 750, pii_content)
    c.save()
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.mark.asyncio
async def test_rag_security_integrity(sample_pdf_with_pii):
    """
    End-to-end security test:
    1. Upload PDF with PII
    2. Verify it's masked in the database (via mock inspection)
    3. Verify LLM response doesn't leak PII (via mock chat)
    """
    
    # Mocking Qdrant and OpenAI to focus on integrity logic
    with patch("src.services.qdrant_service.QdrantClient") as mock_qdrant_client, \
         patch("src.services.qdrant_service.OpenAIEmbeddings.embed_documents") as mock_embed, \
         patch("src.core.logic.retrieval.ChatOpenAI") as mock_llm_class, \
         patch("src.core.logic.retrieval.ChatPromptTemplate.from_messages") as mock_prompt_from:

        # 1. Setup Mock Qdrant behavior
        mock_instance = mock_qdrant_client.return_value
        # Record upserted points for inspection
        captured_points = []
        def side_effect_upsert(collection_name, points):
            nonlocal captured_points
            captured_points.extend(points)
        mock_instance.upsert.side_effect = side_effect_upsert
        
        # Mock embeddings to return dummy vectors
        mock_embed.return_value = [[0.1] * 1536] 

        # 2. Step: Ingest the PDF
        with open(sample_pdf_with_pii, "rb") as f:
            response = client.post("/ingest/file", files={"file": (sample_pdf_with_pii, f, "application/pdf")})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 3. Step: Inspect Database Integrity (Step 3 in user request)
        assert len(captured_points) > 0
        payload = captured_points[0].payload
        text_in_db = payload.get("page_content", "")
        
        # Assertions for masking
        assert "john.doe@example.com" not in text_in_db
        assert "DE89370400440532013000" not in text_in_db
        assert "[EMAIL_MASKED]" in text_in_db
        assert "[IBAN_MASKED]" in text_in_db

        # 4. Step: Verify LLM Retrieval (Step 4 in user request)
        # Mock LLM to simulate grounded response based on MASKED context
        mock_llm = mock_llm_class.return_value
        mock_chain = AsyncMock()
        mock_result = MagicMock()
        # The LLM receives masked context, so it should only see [IBAN_MASKED]
        mock_result.content = "Based on the document, the IBAN is [IBAN_MASKED]. (Source: test_pii_document.pdf, Page: 1)"
        mock_chain.ainvoke.return_value = mock_result
        
        mock_prompt = MagicMock()
        mock_prompt.__or__.return_value = mock_chain
        mock_prompt_from.return_value = mock_prompt

        # Mock Search results to return the masked chunk
        mock_instance.search.return_value = [
            MagicMock(payload=payload)
        ]

        chat_response = client.post("/chat", json={"query": "What is the IBAN in the document?"})
        
        assert chat_response.status_code == 200
        answer = chat_response.json()["answer"]
        assert "DE89370400440532013000" not in answer
        assert "[IBAN_MASKED]" in answer
