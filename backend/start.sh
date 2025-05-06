#!/bin/bash

# Maximum number of retries
MAX_RETRIES=5
# Initial wait time in seconds
WAIT_TIME=10

# Function to check if Neo4j is ready
check_neo4j() {
    python3 - <<EOF
from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "sammy_swipe_secret")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1")
        result.single()
    driver.close()
    exit(0)
except Exception as e:
    print(f"Neo4j not ready: {e}")
    exit(1)
EOF
}

# Function to check if ML models exist
check_ml_models() {
    if [ -f "/app/ml/models/fraud_detection.joblib" ] && \
       [ -f "/app/ml/models/metadata_analyzer.joblib" ] && \
       [ -f "/app/ml/models/matching_model.joblib" ]; then
        return 0
    else
        return 1
    fi
}

# Function to populate database with users from RandomUser API
populate_database() {
    python3 - <<EOF
import asyncio
import os
import sys
sys.path.append('/app')

async def populate():
    try:
        # Import Neo4j client module
        from backend.db.neo4j_client import populate_database_with_random_users
        
        # Number of users to populate
        user_count = int(os.getenv("INITIAL_USER_COUNT", "1000"))
        
        print(f"Populating database with {user_count} users from RandomUser API...")
        
        # Populate the database
        success = await populate_database_with_random_users(user_count)
        
        if success:
            print("Database populated successfully!")
            return 0
        else:
            print("Failed to populate database")
            return 1
    except Exception as e:
        print(f"Error during database population: {e}")
        return 1

# Run the populate function
if __name__ == "__main__":
    result = asyncio.run(populate())
    exit(result)
EOF
}

# Wait for Neo4j to be ready
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if check_neo4j; then
        echo "Neo4j is ready!"
        break
    fi
    echo "Waiting for Neo4j... (Attempt $((retry_count + 1))/$MAX_RETRIES)"
    sleep $WAIT_TIME
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    echo "Failed to connect to Neo4j after $MAX_RETRIES attempts"
    exit 1
fi

# Populate database with users from RandomUser API
echo "Checking if database needs population..."
python3 - <<EOF
import os
import sys
sys.path.append('/app')

try:
    from backend.db.database import db
    
    # Check existing user count
    query = "MATCH (u:User) RETURN count(u) as count"
    result = db.execute_query(query)
    
    if result and result[0]["count"] > 0:
        print(f"Database already contains {result[0]['count']} users.")
        exit(0)
    else:
        print("Database is empty, population needed.")
        exit(1)
except Exception as e:
    print(f"Error checking database: {e}")
    exit(1)
EOF

if [ $? -eq 1 ]; then
    echo "Starting database population..."
    if populate_database; then
        echo "Database population completed successfully!"
    else
        echo "Warning: Database population failed, but continuing startup..."
    fi
else
    echo "Skipping database population as users already exist."
fi

# Initialize ML models and components
echo "Initializing ML components..."
python3 - <<EOF
import os
import sys
sys.path.append('/app')

try:
    # Import the matching service to initialize it
    from backend.ml.matching_service import matching_service
    
    # Test importing our models to make sure they're found
    from backend.ml.models import EnhancedMatchingModel
    
    print("ML matching service initialized successfully!")
    exit(0)
except Exception as e:
    print(f"Error initializing ML components: {str(e)}")
    # Try plain model import as fallback
    try:
        from backend.ml.models import EnhancedMatchingModel
        print("Direct model import successful as fallback")
        exit(0)
    except Exception as e2:
        print(f"Fallback model import also failed: {str(e2)}")
        exit(1)
EOF

if [ $? -eq 0 ]; then
    echo "ML components initialized successfully!"
else
    echo "Warning: ML initialization failed, continuing with basic functionality..."
fi

# Wait for ML models to be available
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if check_ml_models; then
        echo "ML models are ready!"
        break
    fi
    echo "Waiting for ML models... (Attempt $((retry_count + 1))/$MAX_RETRIES)"
    sleep $WAIT_TIME
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    echo "Warning: ML models not found after $MAX_RETRIES attempts. Starting without ML features."
fi

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload 