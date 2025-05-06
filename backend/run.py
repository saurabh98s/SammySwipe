#!/usr/bin/env python3
"""
SammySwipe Backend Server Runner
================================

This script starts the SammySwipe backend server after initializing the database with users
from the RandomUser API. It ensures all necessary components are properly loaded and
database is populated before starting the API server.
"""

import asyncio
import uvicorn
import logging
import time
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("sammyswipe.run")

async def populate_database():
    """Populate the Neo4j database with users from RandomUser API"""
    from db.neo4j_client import populate_database_with_random_users
    
    # Number of users to populate
    user_count = int(os.getenv("INITIAL_USER_COUNT", "1000"))
    
    logger.info(f"Populating database with {user_count} users...")
    start_time = time.time()
    
    # Populate the database
    success = await populate_database_with_random_users(user_count)
    
    elapsed_time = time.time() - start_time
    if success:
        logger.info(f"Database populated successfully in {elapsed_time:.2f} seconds")
    else:
        logger.error(f"Failed to populate database after {elapsed_time:.2f} seconds")
        
    return success

async def check_database_connection():
    """Check if the Neo4j database connection is working properly"""
    try:
        from db.database import db
        
        # Simple query to check connection
        query = "MATCH (n) RETURN count(n) as count LIMIT 1"
        result = db.execute_query(query)
        
        if result is not None:
            logger.info(f"Database connection successful. Found {result[0]['count']} nodes.")
            return True
        else:
            logger.error("Database query returned None result")
            return False
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

async def initialize_ml_models():
    """Initialize the ML models for matching"""
    try:
        # Import the matching service to initialize it
        from ml.matching_service import matching_service
        
        logger.info("ML models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize ML models: {str(e)}")
        return False

async def setup():
    """Run all setup tasks before starting the server"""
    # Load environment variables
    load_dotenv()
    
    # Check database connection
    db_connected = await check_database_connection()
    if not db_connected:
        logger.error("Database connection failed, cannot continue")
        return False
    
    # Populate database with users if needed
    db_populated = await populate_database()
    if not db_populated:
        logger.warning("Database population failed, continuing anyway")
    
    # Initialize ML models
    ml_initialized = await initialize_ml_models()
    if not ml_initialized:
        logger.warning("ML models initialization failed, continuing with basic matching")
    
    return True

def start_server():
    """Start the Uvicorn server with the FastAPI application"""
    # Get server configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "False").lower() == "true"
    
    logger.info(f"Starting SammySwipe backend server on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

async def main():
    """Main entry point for running the server"""
    # Run setup tasks
    setup_success = await setup()
    
    if not setup_success:
        logger.error("Setup failed, exiting")
        return
    
    logger.info("Setup completed successfully, starting server")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 