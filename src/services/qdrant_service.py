import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.core.config import settings

logger = structlog.get_logger()

class VectorStoreService:
    def __init__(self):
        try:
            self.client = QdrantClient(url=settings.QDRANT_URL)
            self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            self.collection_name = settings.COLLECTION_NAME
            self._ensure_collection()
        except Exception as e:
            logger.error("qdrant_init_failed", error=str(e))
            raise

    def _ensure_collection(self):
        """Ensures the collection exists in Qdrant."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                logger.info("creating_collection", name=self.collection_name)
                # Assuming 1536 dimensions for OpenAI text-embedding-3-small or text-embedding-ada-002
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
                )
        except Exception as e:
            logger.error("collection_check_failed", error=str(e))
            # Don't raise here if it's a connection issue, it might be handled in upsert

    def upsert_documents(self, documents: list[Document]):
        """
        Generates embeddings and stores documents in Qdrant.
        Includes error handling for connection issues.
        """
        if not documents:
            return

        try:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            logger.info("generating_embeddings", count=len(texts))
            embeddings = self.embeddings.embed_documents(texts)
            
            points = [
                models.PointStruct(
                    id=doc.metadata.get("chunk_id", i), # fallback to index if no chunk_id
                    vector=embeddings[i],
                    payload=metadatas[i]
                )
                for i, doc in enumerate(documents)
            ]
            
            logger.info("upserting_to_qdrant", count=len(points))
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            logger.error("upsert_failed", error=str(e))
            raise ConnectionError(f"Failed to upsert to Qdrant: {e}")
            
    def close(self):
        self.client.close()
