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
password = os.getenv("NEO4J_PASSWORD", "password")

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