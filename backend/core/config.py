from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "SammySwipe"
    API_V1_STR: str = "/api/v1"
    
    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "sammy_swipe_secret")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # ML Model settings
    MODEL_PATH: str = "ml/models"
    
    # Database population settings
    POPULATE_DB_ON_STARTUP: bool = os.getenv("POPULATE_DB_ON_STARTUP", "True").lower() == "true"
    RANDOM_USER_COUNT: int = int(os.getenv("RANDOM_USER_COUNT", "1000"))
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings() 