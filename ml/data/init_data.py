import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from neo4j import GraphDatabase
import json
import uuid
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataInitializer:
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "sammy_swipe_secret")
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

    def download_sample_data(self):
        """Download sample dating profiles dataset."""
        # Using a sample dating profiles dataset from Kaggle
        # For this example, we'll create synthetic data similar to dating app profiles
        
        num_profiles = 1000
        interests = [
            "Travel", "Music", "Movies", "Sports", "Reading", "Gaming",
            "Cooking", "Photography", "Art", "Technology", "Fitness",
            "Dancing", "Hiking", "Fashion", "Food", "Animals"
        ]
        
        data = []
        now = datetime.now()
        
        for _ in range(num_profiles):
            birth_date = now - timedelta(days=np.random.randint(365*18, 365*60))
            num_interests = np.random.randint(2, 7)
            profile_interests = np.random.choice(interests, num_interests, replace=False).tolist()
            
            profile = {
                "id": str(uuid.uuid4()),
                "email": f"user_{_}@example.com",
                "username": f"user_{_}",
                "full_name": f"User {_}",
                "gender": np.random.choice(["male", "female", "non_binary", "other"]),
                "birth_date": birth_date.isoformat(),
                "bio": f"Sample bio for user {_}. Interests include {', '.join(profile_interests)}.",
                "interests": profile_interests,
                "location": np.random.choice(["New York", "London", "Tokyo", "Paris", "Berlin"]),
                "created_at": (now - timedelta(days=np.random.randint(1, 365))).isoformat(),
                "login_frequency": np.random.randint(1, 100),
                "profile_updates": np.random.randint(0, 10),
                "reported_count": np.random.randint(0, 3),
                "suspicious_login_count": np.random.randint(0, 2),
                "message_count": np.random.randint(0, 200),
                "matches_count": np.random.randint(0, 50),
                "match_acceptance_rate": np.random.random(),
                "response_rate": np.random.random(),
                "avg_message_length": np.random.randint(10, 100),
                "profile_completeness": np.random.random()
            }
            data.append(profile)
        
        # Save to disk
        os.makedirs("ml/data", exist_ok=True)
        with open("ml/data/sample_profiles.json", "w") as f:
            json.dump(data, f)
        
        return data

    def create_constraints(self):
        """Create Neo4j constraints."""
        constraints = [
            "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                session.run(constraint)

    def import_data(self, data: List[Dict]):
        """Import data into Neo4j."""
        # Create users
        query = """
        UNWIND $profiles as profile
        CREATE (u:User {
            id: profile.id,
            email: profile.email,
            username: profile.username,
            full_name: profile.full_name,
            gender: profile.gender,
            birth_date: datetime(profile.birth_date),
            bio: profile.bio,
            interests: profile.interests,
            location: profile.location,
            created_at: datetime(profile.created_at),
            login_frequency: profile.login_frequency,
            profile_updates: profile.profile_updates,
            reported_count: profile.reported_count,
            suspicious_login_count: profile.suspicious_login_count,
            message_count: profile.message_count,
            matches_count: profile.matches_count,
            match_acceptance_rate: profile.match_acceptance_rate,
            response_rate: profile.response_rate,
            avg_message_length: profile.avg_message_length,
            profile_completeness: profile.profile_completeness,
            is_active: true,
            is_verified: true
        })
        """
        
        with self.driver.session() as session:
            session.run(query, {"profiles": data})
        
        # Create some matches and messages
        query = """
        MATCH (u1:User), (u2:User)
        WHERE u1 <> u2 AND rand() < 0.1
        WITH u1, u2 LIMIT 5000
        CREATE (u1)-[r:MATCHED {
            score: rand(),
            created_at: datetime(),
            status: 'accepted',
            accepted_at: datetime()
        }]->(u2)
        """
        
        with self.driver.session() as session:
            session.run(query)

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

def main():
    initializer = DataInitializer()
    try:
        logger.info("Creating constraints...")
        initializer.create_constraints()
        
        logger.info("Downloading sample data...")
        data = initializer.download_sample_data()
        
        logger.info("Importing data into Neo4j...")
        initializer.import_data(data)
        
        logger.info("Data initialization completed successfully!")
    except Exception as e:
        logger.error(f"Error during data initialization: {e}")
        raise
    finally:
        initializer.close()

if __name__ == "__main__":
    main() 