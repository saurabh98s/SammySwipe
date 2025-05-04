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

from db.neo4j_client import populate_database_with_random_users
from core.config import get_settings

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
    
    logger.info(f"Starting population of Neo4j database with {user_count} random users")
    
    # Populate the database
    success = await populate_database_with_random_users(user_count)
    
    if success:
        logger.info(f"Successfully populated Neo4j database with {user_count} random users")
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
    asyncio.run(main()) 