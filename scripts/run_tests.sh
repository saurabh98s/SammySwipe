#!/bin/bash

# Run auth tests in the backend container
docker compose exec backend pytest /app/backend/tests/test_auth.py -v --cov=/app/backend/api/auth.py --cov-report=term-missing 