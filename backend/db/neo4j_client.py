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
    """
    try:
        logger.info(f"Storing {len(users)} users in Neo4j")
        
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        # Define the Cypher query for user batch creation
        query = """
        UNWIND $users as user
        MERGE (u:User {id: user.id})
        ON CREATE SET 
            u.email = user.email,
            u.username = user.username,
            u.full_name = user.full_name,
            u.gender = user.gender,
            u.birth_date = user.birth_date,
            u.location = user.location,
            u.profile_photo = user.profile_photo,
            u.interests = user.interests,
            u.bio = user.bio,
            u.created_at = datetime(),
            u.updated_at = datetime(),
            u.is_active = true,
            u.is_verified = true,
            u.login_frequency = 0,
            u.profile_updates = 0,
            u.reported_count = 0,
            u.suspicious_login_count = 0,
            u.match_score = user.match_score
        """
        
        # Create batches of 100 users to avoid memory issues
        batch_size = 100
        for i in range(0, len(users), batch_size):
            batch = users[i:i+batch_size]
            user_batch = []
            
            for user in batch:
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
                    "match_score": round(float(abs(int(user["location"]["coordinates"]["latitude"]))) / 100.0, 2) % 1.0,
                    "bio": f"Hi, I'm {user['name']['first']}! I'm from {user['location']['city']} and enjoy meeting new people."
                }
                
                # Ensure match score is between 0.4 and 0.95
                if user_data["match_score"] < 0.4:
                    user_data["match_score"] += 0.4
                elif user_data["match_score"] > 0.95:
                    user_data["match_score"] = 0.95
                    
                user_batch.append(user_data)
            
            # Execute batch creation in database
            db.execute_query(query, {"users": user_batch})
            logger.info(f"Stored batch of {len(user_batch)} users (total progress: {i+len(batch)}/{len(users)})")
        
        logger.info(f"Successfully stored all {len(users)} users in Neo4j")
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
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        logger.info(f"Skipping database population in superadmin mode")
        return True
        
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
    Retrieve a single random user from RandomUser.me
    and generate demo “raw social” data (tweets/posts) for them.
    """
    # Fetch exactly one random user
    users = await fetch_random_users(1)
    if not users:
        return {}

    u = users[0]
    first = u["name"]["first"]
    city  = u["location"]["city"]
    country = u["location"]["country"]

    # Build templated posts using that real user’s name & location
    twitter_posts = [
        {"text": f"Hey, I'm {first} from {city}! Loving this new app. #social #demo"},
        {"text": f"Just explored {city}, {country}—absolutely stunning! 🌄 #travel"},
        {"text": f"Tech geek alert 🚨 Trying out the latest gadget. #innovation"}
    ]
    instagram_posts = [
        {"caption": f"Sunset over {city} is unreal 🌅 #nofilter"},
        {"caption": f"Coffee and code ☕💻 #developerLife"},
        {"caption": f"Weekend hike — nature therapy! #outdoors"}
    ]
    facebook_posts = [
        {"message": f"Family dinner in {city} was delightful! #foodie"},
        {"message": f"Completed my first 5K today — feeling energized! 🏃‍♂️"},
        {"message": f"Movie night with friends 🍿🎬 #relax"}
    ]

    return {
        "twitter":   {"tweets": twitter_posts},
        "instagram": {"media": {"data": instagram_posts}},
        "facebook":  {"posts": {"data": facebook_posts}}
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
    Fetch one random user, then generate
    4–7 topic affinities using your interest generator.
    """
    import random

    # Grab one fresh profile
    users = await fetch_random_users(1)
    if not users:
        return {}

    # Pick 4–7 interests for “this” user
    interests = generate_random_interests_for_user()
    selected = random.sample(interests, k=random.randint(4, len(interests)))

    # Assign each a random score 0.5–0.95
    topics = {
        topic: round(random.uniform(0.5, 0.95), 2)
        for topic in selected
    }

    # Return sorted descending by score
    return dict(sorted(topics.items(), key=lambda kv: kv[1], reverse=True))

async def get_recommendations_for_user(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    For demo (or in SUPERADMIN_MODE), fetch `limit`
    profiles via RandomUser.me and turn them into
    “match” recommendations with real names/photos
    plus generated interests and scores.
    """
    # If real DB mode, you’d run a Cypher MATCH here; else:
    users = await fetch_random_users(limit)
    recs = []

    for u in users:
        first = u["name"]["first"]
        city  = u["location"]["city"]
        country = u["location"]["country"]
        # Base payload
        rec = {
            "id": u["login"]["uuid"],
            "full_name": f"{first} {u['name']['last']}",
            "bio":     f"Hi, I'm {first} from {city}! Nice to meet you.",
            "interests": generate_random_interests_for_user(),
            "location": f"{city}, {country}",
            "birth_date": u["dob"]["date"],
            "profile_photo": u["picture"]["large"],
            # Derive a pseudo “match_score” from latitude
            "match_score": None,
            "common_topics": None
        }
        # A quick match_score in [.4, .95]
        raw = abs(int(float(u["location"]["coordinates"]["latitude"])))
        ms = (raw % 100) / 100.0
        rec["match_score"] = min(max(ms, 0.4), 0.95)

        # Pick 3 “common” topics
        rec["common_topics"] = generate_random_interests_for_user()[:3]
        recs.append(rec)

    # Sort top to bottom
    recs.sort(key=lambda x: x["match_score"], reverse=True)
    return recs
