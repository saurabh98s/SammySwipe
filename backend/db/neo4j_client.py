import json
from typing import Dict, Any, List
import os
import logging
import requests
from datetime import datetime

# In a real implementation, this would connect to a Neo4j instance
# For this demonstration, we'll simply log the operations

logger = logging.getLogger(__name__)

# RandomUser API URL
RANDOM_USER_API = "https://randomuser.me/api/"

async def fetch_random_users(count: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetch a specified number of random users from the RandomUser API
    
    Args:
        count: Number of users to fetch (max 5000 per request)
        
    Returns:
        List of user dictionaries
    """
    try:
        # Fetch random users with all details
        response = requests.get(f"{RANDOM_USER_API}?results={count}&nat=us,gb,ca,au,fr,de")
        data = response.json()
        
        if "results" not in data:
            logger.error("Failed to fetch random users: Invalid response format")
            return []
            
        logger.info(f"Successfully fetched {len(data['results'])} random users")
        return data["results"]
    except Exception as e:
        logger.error(f"Error fetching random users: {str(e)}")
        return []

async def store_random_users_in_neo4j(users: List[Dict[str, Any]]) -> bool:
    """
    Store random users in Neo4j database
    
    In a real implementation, this would create User nodes in Neo4j
    """
    try:
        logger.info(f"Storing {len(users)} users in Neo4j")
        
        # In a real implementation, we would use a batch operation to store all users
        # For demonstration, we'll just log the operation
        
        for user in users:
            # Extract relevant user data
            user_data = {
                "id": user["login"]["uuid"],
                "email": user["email"],
                "username": user["login"]["username"],
                "full_name": f"{user['name']['first']} {user['name']['last']}",
                "gender": user["gender"],
                "birth_date": user["dob"]["date"],
                "location": f"{user['location']['city']}, {user['location']['country']}",
                "profile_photo": user["picture"]["large"],
                "interests": generate_random_interests_for_user(),
                "match_score": round(float(user["location"]["coordinates"]["latitude"]) / 100.0, 2),
                "bio": f"Hi, I'm {user['name']['first']}! I'm from {user['location']['city']} and enjoy meeting new people."
            }
            
            # Log user creation (in real implementation, we would create a user node)
            logger.debug(f"Creating user: {user_data['full_name']} ({user_data['email']})")
            
            # Create Cypher query for user creation
            # MERGE (u:User {id: $id})
            # SET u.email = $email, u.username = $username, ... (other properties)
            
        return True
    except Exception as e:
        logger.error(f"Error storing random users in Neo4j: {str(e)}")
        return False

def generate_random_interests_for_user() -> List[str]:
    """Generate a list of random interests for a user"""
    all_interests = [
        "Travel", "Photography", "Cooking", "Fitness", "Reading", 
        "Art", "Music", "Movies", "Gaming", "Technology", 
        "Fashion", "Hiking", "Yoga", "Dancing", "Writing",
        "Swimming", "Running", "Cycling", "Skiing", "Climbing",
        "Food", "Coffee", "Wine", "Beer", "Cocktails"
    ]
    
    # Get 3-7 random interests
    import random
    num_interests = random.randint(3, 7)
    return random.sample(all_interests, num_interests)

async def populate_database_with_random_users(count: int = 1000) -> bool:
    """
    Fetch random users and populate the Neo4j database
    
    Args:
        count: Number of users to fetch and store
        
    Returns:
        True if successful, False otherwise
    """
    # Fetch users from RandomUser API
    users = await fetch_random_users(count)
    
    if not users:
        logger.error("Failed to fetch random users")
        return False
        
    # Store users in Neo4j
    return await store_random_users_in_neo4j(users)

async def store_social_raw_data(user_id: str, source: str, data: Dict[str, Any]) -> bool:
    """
    Store raw social media data in Neo4j
    
    In a real implementation, this would create:
    CREATE (u:User {id:user_id})-[:RAW_INTEREST {source:source}]->(r:RawBlob {data: json_data})
    """
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Log the operation (in a real implementation, this would store in Neo4j)
        logger.info(f"Storing raw {source} data for user {user_id}")
        logger.debug(f"Data: {json_data[:100]}...")  # Log just the beginning to avoid logging sensitive data
        
        # In a real implementation, we would execute a Cypher query to Neo4j:
        # MATCH (u:User {id: $user_id})
        # MERGE (u)-[:RAW_INTEREST {source: $source}]->(r:RawBlob)
        # SET r.data = $json_data
        # RETURN r
        
        return True
    except Exception as e:
        logger.error(f"Error storing social data: {str(e)}")
        return False

async def get_user_raw_interests(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user's raw social media data from Neo4j
    
    In a real implementation, this would execute:
    MATCH (u:User {id:user_id})-[:RAW_INTEREST]->(r:RawBlob)
    RETURN r.data, r.source
    """
    # For demonstration, return more realistic data
    return {
        "twitter": {
            "tweets": [
                {"text": "Just started using SammySwipe! Can't wait to meet new people. #dating #tech"},
                {"text": "Visited the Grand Canyon this weekend. Absolutely breathtaking views! #travel #adventure"},
                {"text": "New gadgets are always fun to try out! Currently testing the latest smartphone #technology"}
            ]
        },
        "instagram": {
            "media": {
                "data": [
                    {"caption": "Beautiful sunset at Malibu Beach! The colors were incredible 🌅 #travel #sunset #beach"},
                    {"caption": "Tried this new restaurant downtown. The food was absolutely amazing! 🍕🍷 #food #foodie"},
                    {"caption": "Mountain hiking trip with friends - reached the summit! 🏔️ #nature #hiking #mountains"}
                ]
            }
        },
        "facebook": {
            "posts": {
                "data": [
                    {"message": "Enjoying the weekend with friends at the lake house! Such a refreshing getaway."},
                    {"message": "Just discovered this amazing coffee shop downtown. Their lattes are to die for!"},
                    {"message": "Completed my first half marathon today! So proud of this achievement 🏃‍♂️"}
                ]
            }
        }
    }

async def store_user_topics(user_id: str, topics: Dict[str, float]) -> bool:
    """
    Store user topic affinities in Neo4j
    
    In a real implementation, this would create:
    MATCH (u:User {id:user_id})
    MERGE (t:Topic {name:topic_name})
    CREATE (u)-[:HAS_TOPIC {score:score}]->(t)
    """
    try:
        # Log the operation (in a real implementation, this would store in Neo4j)
        logger.info(f"Storing topics for user {user_id}")
        logger.debug(f"Topics: {topics}")
        
        # In a real implementation, we would execute Cypher queries to Neo4j
        return True
    except Exception as e:
        logger.error(f"Error storing user topics: {str(e)}")
        return False

async def get_user_topics(user_id: str) -> Dict[str, float]:
    """
    Retrieve user's topics from Neo4j
    
    In a real implementation, this would execute:
    MATCH (u:User {id:user_id})-[r:HAS_TOPIC]->(t:Topic)
    RETURN t.name, r.score
    """
    # For demonstration, return more realistic data with varied topics
    import random
    
    # List of potential topics with score ranges
    potential_topics = {
        "Travel": (0.7, 0.95),
        "Photography": (0.6, 0.9),
        "Food & Dining": (0.65, 0.85),
        "Music": (0.5, 0.85),
        "Movies": (0.6, 0.8),
        "Reading": (0.5, 0.8),
        "Sports": (0.5, 0.9),
        "Fitness": (0.6, 0.9),
        "Technology": (0.65, 0.9),
        "Art": (0.5, 0.85),
        "Fashion": (0.5, 0.8),
        "Gaming": (0.6, 0.9),
        "Cooking": (0.6, 0.85),
        "Outdoors": (0.65, 0.9),
    }
    
    # Select 4-8 random topics
    selected_topics = random.sample(list(potential_topics.keys()), random.randint(4, 8))
    
    # Generate random scores within the defined ranges
    result = {}
    for topic in selected_topics:
        min_score, max_score = potential_topics[topic]
        result[topic] = round(random.uniform(min_score, max_score), 2)
    
    # Sort by score descending
    return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

async def get_recommendations_for_user(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get personalized match recommendations for a user
    
    In a real implementation, this would query Neo4j for potential matches
    based on interests, location, and other factors
    
    Args:
        user_id: ID of the user to get recommendations for
        limit: Maximum number of recommendations to return
        
    Returns:
        List of potential matches with match scores
    """
    # For demonstration, return random users with random match scores
    users = await fetch_random_users(limit)
    recommendations = []
    
    for user in users:
        # Create a match recommendation
        match = {
            "id": user["login"]["uuid"],
            "full_name": f"{user['name']['first']} {user['name']['last']}",
            "bio": f"Hi, I'm {user['name']['first']}! I'm from {user['location']['city']} and enjoy meeting new people.",
            "interests": generate_random_interests_for_user(),
            "location": f"{user['location']['city']}, {user['location']['country']}",
            "birth_date": user["dob"]["date"],
            "profile_photo": user["picture"]["large"],
            "match_score": round(float(abs(int(user["location"]["coordinates"]["latitude"]))) / 100.0, 2) % 1.0,
            "common_topics": generate_random_interests_for_user()[:3]  # Common topics/interests
        }
        
        # Ensure match score is between 0.4 and 0.95
        if match["match_score"] < 0.4:
            match["match_score"] += 0.4
        elif match["match_score"] > 0.95:
            match["match_score"] = 0.95
        
        recommendations.append(match)
    
    # Sort by match score (descending)
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    return recommendations 