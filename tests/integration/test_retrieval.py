import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from langchain_core.documents import Document
from src.core.logic.retrieval import generate_answer

@pytest.mark.asyncio
async def test_generate_answer_success():
    # 1. Mock VectorStoreService and its query_similar_chunks method
    mock_chunks = [
        Document(
            page_content="The policy covers dental care up to 500 EUR.", 
            metadata={"source_file": "policy.pdf", "page_number": 1}
        )
    ]
    
    with patch("src.core.logic.retrieval.VectorStoreService") as mock_vss_class:
        mock_vss = MagicMock()
        mock_vss.query_similar_chunks.return_value = mock_chunks
        mock_vss_class.return_value = mock_vss
        
        # 2. Mock ChatOpenAI's chain execution
        with patch("src.core.logic.retrieval.ChatOpenAI") as mock_llm_class:
            mock_llm = MagicMock()
            # ainvoke returns a message-like object with .content
            mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="The policy covers dental care up to 500 EUR. (Source: policy.pdf, Page: 1)"))
            
            # Using prompt | llm syntax means we have to mock the Runnables as well if we don't mock the whole chain.
            # I'll mock ChatPromptTemplate and the chain to simplify.
            with patch("src.core.logic.retrieval.ChatPromptTemplate.from_messages") as mock_prompt_from:
                mock_prompt = MagicMock()
                mock_prompt_from.return_value = mock_prompt
                
                # mock_prompt | mock_llm
                mock_chain = AsyncMock()
                mock_chain.ainvoke.return_value = MagicMock(content="The policy covers dental care up to 500 EUR. (Source: policy.pdf, Page: 1)")
                mock_prompt.__or__.return_value = mock_chain
                
                # Execute
                result = await generate_answer("What does dental care cover?")
                
                assert "answer" in result
                assert "dental care up to 500 EUR" in result["answer"]
                assert result["sources"][0]["file"] == "policy.pdf"

@pytest.mark.asyncio
async def test_generate_answer_not_found():
    # Mock VectorStoreService to return no chunks
    with patch("src.core.logic.retrieval.VectorStoreService") as mock_vss_class:
        mock_vss = MagicMock()
        mock_vss.query_similar_chunks.return_value = []
        mock_vss_class.return_value = mock_vss
        
        # Execute
        result = await generate_answer("What about car insurance?")
        
        assert "couldn't find any relevant information" in result["answer"]
        assert len(result["sources"]) == 0
