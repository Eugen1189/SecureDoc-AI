from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    QDRANT_URL: str = "http://qdrant:6333"
    COLLECTION_NAME: str = "securedoc_collection"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
