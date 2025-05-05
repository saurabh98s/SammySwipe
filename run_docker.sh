#!/bin/bash

echo "Building and starting SammySwipe application in Docker..."

# Build the containers
docker-compose build

# Start the containers in detached mode
docker-compose up -d

echo "Waiting for services to start up..."
sleep 10

echo "Neo4j Database: http://localhost:7474/browser/"
echo "Backend API: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"

echo "Docker containers are running!"
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down" 