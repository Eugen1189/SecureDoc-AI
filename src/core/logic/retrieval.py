import structlog
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.services.qdrant_service import VectorStoreService
from src.core.config import settings

logger = structlog.get_logger()

SYSTEM_PROMPT = """
You are a secure document analysis assistant. Use the provided context to answer the user's question.

RULES:
1. Answer ONLY based on the provided context. If the information is not in the context, say "I don't know based on the provided documents."
2. You MUST include citations for every claim you make.
3. Citation format: (Source: [filename], Page: [number]).
4. Stay professional and concise.

CONTEXT:
{context}
"""

async def generate_answer(user_query: str) -> dict:
    """
    RAG Orchestrator:
    Retrieve relevant chunks -> Format context -> Generate answer with citations.
    """
    vector_service = VectorStoreService()
    try:
        # 1. Retrieve relevant chunks
        chunks = vector_service.query_similar_chunks(user_query, top_k=4)
        
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the documents.",
                "sources": []
            }

        # 2. Format context and collect unique sources
        context_parts = []
        sources = []
        for chunk in chunks:
            source_info = f"Source: {chunk.metadata.get('source_file')}, Page: {chunk.metadata.get('page_number')}"
            context_parts.append(f"[{source_info}]\nContent: {chunk.page_content}")
            
            # Simple list of sources for the response
            sources.append({
                "file": chunk.metadata.get("source_file"),
                "page": chunk.metadata.get("page_number")
            })

        context_str = "\n\n".join(context_parts)

        # 3. Generate answer using LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{query}")
        ])
        
        chain = prompt | llm
        
        logger.info("generating_llm_response", query=user_query)
        response = await chain.ainvoke({"context": context_str, "query": user_query})
        
        return {
            "answer": response.content,
            "sources": sources
        }
        
    except Exception as e:
        logger.error("rag_generation_failed", error=str(e))
        raise
    finally:
        vector_service.close()
