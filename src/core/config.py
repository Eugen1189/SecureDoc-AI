from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    QDRANT_URL: str = "http://qdrant:6333"
    COLLECTION_NAME: str = "securedoc_collection"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
