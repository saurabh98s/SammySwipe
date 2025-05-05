#!/bin/bash

echo "Populating Neo4j database with 1000 users..."

# Execute the populate_users.py script inside the backend container
docker exec -it sammyswipe-backend python -m scripts.populate_users --count 1000

echo "Database population completed!" 