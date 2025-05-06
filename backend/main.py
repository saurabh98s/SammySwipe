from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .db.database import db
from .api import auth, users, matches, chat, health
from .db.neo4j_client import populate_database_with_random_users
import asyncio
import logging

# Import our ML service for initialization
from .ml.matching_service import matching_service
from .services.ml_integration import ml_service

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(matches.router, prefix=settings.API_V1_STR, tags=["matches"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])

@app.on_event("startup")
async def startup_event():
    # Set up logging for the app
    logger = logging.getLogger("uvicorn")
    
    # Create database constraints
    try:
        db.create_constraints()
        logger.info("Database constraints created successfully")
    except Exception as e:
        logger.error(f"Failed to create database constraints: {str(e)}")
    
    # Populate the database with random users if enabled
    if settings.POPULATE_DB_ON_STARTUP:
        try:
            # Check if database already has users
            query = "MATCH (u:User) RETURN count(u) as user_count"
            result = db.execute_query(query)
            existing_users = result[0]["user_count"] if result else 0
            
            if existing_users > 20000:
                logger.info(f"Database already contains {existing_users} users. Skipping population.")
            else:
                logger.info(f"Populating database with {settings.RANDOM_USER_COUNT} random users...")
                # Starting population process in the background
                asyncio.create_task(populate_database_with_random_users(settings.RANDOM_USER_COUNT))
                logger.info("User population task started in the background")
        except Exception as e:
            logger.error(f"Failed to initiate database population: {str(e)}")
    else:
        logger.info("Automatic database population is disabled")
    
    # Initialize ML components
    try:
        # The matching_service is already initialized when imported
        logger.info("ML matching service initialized successfully")
        
        # Initialize NLTK for text analysis if needed
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading required NLTK data...")
            nltk.download('punkt')
            nltk.download('stopwords')
            logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ML components: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to SammySwipe API"} 