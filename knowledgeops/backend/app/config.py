import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "KnowledgeOps"
    debug: bool = False
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3"
    llm_timeout_s: float = 60.0
    evalops_base_url: str = "http://localhost:8000"
    sentinelai_base_url: str = ""
    vector_model: str = "all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    class Config:
        env_prefix = "KNOWLEDGEOPS_"
        env_file = ".env"


settings = Settings()
