#!/usr/bin/env python3
"""
Script to populate Neo4j database with random users from RandomUser API.
This can be run independently to pre-populate the database.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the parent directory to the path so we can import modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from db.neo4j_client import populate_database_with_random_users, fetch_random_users
from core.config import get_settings
from db.database import db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the script."""
    settings = get_settings()
    user_count = settings.RANDOM_USER_COUNT
    
    # Create Neo4j constraints if they don't exist
    logger.info("Creating Neo4j constraints...")
    db.create_constraints()
    
    # Check if we already have users in the database
    logger.info("Checking existing users in the database...")
    query = "MATCH (u:User) RETURN count(u) as user_count"
    result = db.execute_query(query)
    existing_users = result[0]["user_count"] if result else 0
    
    logger.info(f"Found {existing_users} existing users in the database")
    
    if existing_users > 0:
        logger.info("Database already contains users. Do you want to:")
        logger.info("1. Add more users")
        logger.info("2. Replace all users")
        logger.info("3. Exit")
        
        try:
            choice = input("Enter your choice (1/2/3): ")
            
            if choice == "1":
                logger.info(f"Adding {user_count} more users to the database")
                # Continue with adding users
            elif choice == "2":
                logger.info("Removing all existing users from the database")
                delete_query = "MATCH (u:User) DELETE u"
                db.execute_query(delete_query)
                logger.info("All users deleted")
            else:
                logger.info("Exiting without changes")
                return
        except KeyboardInterrupt:
            logger.info("\nExiting without changes")
            return
    
    logger.info(f"Starting population of Neo4j database with {user_count} random users")
    
    # Fetch random users
    users = await fetch_random_users(user_count)
    logger.info(f"Successfully fetched {len(users)} random users from API")
    
    if not users:
        logger.error("Failed to fetch random users")
        return
    
    # Populate the database
    success = await populate_database_with_random_users(user_count)
    
    if success:
        logger.info(f"Successfully populated Neo4j database with {user_count} random users")
        
        # Verify the total number of users in the database
        query = "MATCH (u:User) RETURN count(u) as user_count"
        result = db.execute_query(query)
        total_users = result[0]["user_count"] if result else 0
        
        logger.info(f"Total users in database: {total_users}")
    else:
        logger.error("Failed to populate Neo4j database with random users")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Populate Neo4j database with random users')
    parser.add_argument('--count', type=int, default=1000, help='Number of users to fetch and store')
    args = parser.parse_args()
    
    # Override user count with command line argument if provided
    os.environ["RANDOM_USER_COUNT"] = str(args.count)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1) 