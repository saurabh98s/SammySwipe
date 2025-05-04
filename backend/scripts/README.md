# SammySwipe Backend Scripts

This directory contains utility scripts for the SammySwipe backend.

## User Population Script

The `populate_users.py` script is used to populate the Neo4j database with random users from the RandomUser API. This can be useful for development, testing, and demonstration purposes.

### Usage

```bash
# Populate with default 1000 users
python populate_users.py

# Specify a custom number of users
python populate_users.py --count 500
```

### Configuration

You can configure the behavior of the script through environment variables or the `.env` file:

- `POPULATE_DB_ON_STARTUP`: Set to "True" to automatically populate the database on application startup (default: "True")
- `RANDOM_USER_COUNT`: Number of random users to fetch and store (default: 1000)

## Notes

- The script fetches user data from the RandomUser API (https://randomuser.me)
- Users are stored in the Neo4j database with realistic profiles
- Each user is assigned random interests and other attributes
- The script handles pagination for large user counts
- The script is idempotent and can be run multiple times without creating duplicate users

## Dependencies

- requests: For fetching data from the RandomUser API
- asyncio: For asynchronous operations
- logging: For detailed logs during execution 