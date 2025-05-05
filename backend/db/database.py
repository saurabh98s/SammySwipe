from neo4j import GraphDatabase
from ..core.config import get_settings
from typing import Any, List, Dict
import os
import json
import random
from datetime import datetime, timedelta
import logging
import requests
logger = logging.getLogger(__name__)
settings = get_settings()

class Neo4jDatabase:
    def __init__(self):
        self._driver = None
        self._superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"

    def connect(self):
        if not self._driver:
            try:
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
            except Exception as e:
                if self._superadmin_mode:
                    logger.warning(f"Failed to connect to Neo4j: {str(e)}. Using mock data in superadmin mode.")
                else:
                    raise
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, parameters: dict = None) -> list[dict[str, Any]]:
        # In superadmin mode, return mock data instead of executing real queries
        if self._superadmin_mode:
            return self._mock_query_response(query, parameters or {})
        
        try:
            with self.connect().session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            if self._superadmin_mode:
                logger.info("Returning mock data due to database error in superadmin mode")
                return self._mock_query_response(query, parameters or {})
            raise

    def _mock_query_response(self, query: str, parameters: dict) -> List[Dict[str, Any]]:
        """Generate mock data based on the query"""
        logger.info(f"Generating mock data for query: {query[:100]}...")
        
        # Check for match recommendations query
        if "MATCH (u:User {email: $email})" in query and "return u.preferences" in query.lower():
            return [{"u.preferences": {
                "min_age": 18,
                "max_age": 50,
                "preferred_gender": ["male", "female"],
                "max_distance": 50,
                "interests_weight": 0.7
            }}]
            
        # Check for my-pending-likes query
        if "MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User)" in query and "r.status = 'pending'" in query:
            return self._generate_mock_pending_likes()
        
        # Check for user data query
        if "MATCH (u:User)" in query and "u.gender" in query:
            return self._generate_mock_users(10)
            
        # Check for match scores
        if "MATCH (u:User {id: $user_id})" in query and "u.match_score" in query:
            return [{"score": 0.75}]
        
        # Default response for other queries
        return []
        
    def _generate_mock_users(self, count=10) -> List[Dict[str, Any]]:
        raw_users = self._fetch_random_users(count)
        users = []
        for u in raw_users:
            users.append({
                "user_data": {
                    "id": u["login"]["uuid"],  # unique identifier :contentReference[oaicite:6]{index=6}
                    "email": u["email"],
                    "username": u["login"]["username"],
                    "full_name": f"{u['name']['first']} {u['name']['last']}",
                    "gender": u["gender"],
                    "birth_date": u["dob"]["date"],
                    "bio": "",  # Optionally generate via a template or AI
                    "interests": random.sample(
                        ["Travel", "Music", "Technology", "Sports", "Art"],
                        k=random.randint(1, 3)
                    ),
                    "location": f"{u['location']['city']}, {u['location']['country']}",
                    "profile_photo": u["picture"]["thumbnail"],
                    # App-specific metrics
                    "matches_count": random.randint(5, 20),
                    "message_count": random.randint(10, 100),
                    "avg_message_length": random.randint(10, 50),
                    "login_frequency": random.randint(1, 30),
                    "profile_updates": random.randint(1, 5),
                    "reported_count": 0,
                    "suspicious_login_count": 0
                }
            })
        return users


    def _generate_mock_pending_likes(self, count=5) -> List[Dict[str, Any]]:
        raw_users = self._fetch_random_users(count)
        result = []
        for u in raw_users:
            liked_at = datetime.now() - timedelta(days=random.randint(1, 10))
            result.append({
                "u2": {
                    "id": u["login"]["uuid"],
                    "full_name": f"{u['name']['first']} {u['name']['last']}",
                    "profile_photo": u["picture"]["thumbnail"],
                    "bio": "",
                    "interests": random.sample(
                        ["Travel", "Music", "Technology", "Sports", "Art"],
                        k=random.randint(1, 3)
                    ),
                    "location": f"{u['location']['city']}, {u['location']['country']}",
                    "birth_date": u["dob"]["date"],
                },
                "match_score": round(random.uniform(0.5, 0.95), 2),
                "liked_at": liked_at.isoformat()
            })
        return result


    def create_constraints(self):
        """Create necessary constraints for the database"""
        if self._superadmin_mode:
            logger.info("Skipping constraint creation in superadmin mode")
            return
            
        constraints = [
            "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE"
        ]
        
        try:
            with self.connect().session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                    except Exception as e:
                        print(f"Error creating constraint: {e}")
        except Exception as e:
            logger.error(f"Could not create constraints: {str(e)}")
            if self._superadmin_mode:
                logger.info("Continuing in superadmin mode despite constraint error")
                
    def _fetch_random_users(self, count: int) -> List[Dict[str, Any]]:
        """
        Fetch `count` random users from RandomUser.me, including only the fields
        we need (gender, name, location, email, login, dob, picture, nat).
        """
        url = "https://randomuser.me/api/"
        params = {
            "results": count,             # up to 5000 in one call :contentReference[oaicite:3]{index=3}
            "inc": "gender,name,location,email,login,dob,picture,nat",
            "nat": "us,ca,gb,au"           # fetch from multiple nationalities
        }
        response = requests.get(url, params=params)
        response.raise_for_status()       # HTTP errors as exceptions :contentReference[oaicite:4]{index=4}
        return response.json().get("results", [])  # parse JSON :contentReference[oaicite:5]{index=5}

# Global database instance
db = Neo4jDatabase() 