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

# Start the ML training
echo "Starting ML training..."
python -m ml.training.train 