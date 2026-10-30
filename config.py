import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    SPACY_MODEL: str = "en_core_web_sm"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    SKILLS_DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "skills_master.json")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

