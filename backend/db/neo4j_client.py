import json
from typing import Dict, Any, List
import os
import logging
import requests
from datetime import datetime
import time

# Setup detailed logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# RandomUser API URL
RANDOM_USER_API = "https://randomuser.me/api/"

# Comprehensive user interests
ALL_INTERESTS = [
    "Travel", "Photography", "Cooking", "Fitness", "Reading", 
    "Art", "Music", "Movies", "Gaming", "Technology", 
    "Fashion", "Hiking", "Yoga", "Dancing", "Writing",
    "Swimming", "Running", "Cycling", "Skiing", "Climbing",
    "Food", "Coffee", "Wine", "Beer", "Cocktails",
    "Science", "History", "Philosophy", "Politics", "Economics",
    "Meditation", "Spirituality", "Volunteering", "Animals", "Nature",
    "Cars", "Motorcycles", "DIY", "Gardening", "Painting"
]

# Personality traits for enriched user profiles
PERSONALITY_TRAITS = ["openness", "conscientiousness", "extroversion", "agreeableness", "neuroticism"]

async def fetch_random_users(count: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetch a specified number of random users from the RandomUser API with comprehensive data
    
    Args:
        count: Number of users to fetch (max 5000 per request)
        
    Returns:
        List of user dictionaries
    """
    try:
        logger.info(f"Fetching {count} random users from RandomUser API...")
        
        # Fetch random users with all details
        # Include expanded parameters for more comprehensive data
        response = requests.get(
            RANDOM_USER_API,
            params={
                "results": count,
                "nat": "us,gb,ca,au,fr,de",
                "inc": "gender,name,location,email,login,dob,phone,cell,picture,nat,id"
            }
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        if "results" not in data:
            logger.error("Failed to fetch random users: Invalid response format")
            return []
            
        logger.info(f"Successfully fetched {len(data['results'])} random users")
        logger.info(f"Sample user data: {data['results'][0] if data['results'] else 'No users'}")
        
        # Basic validation of the response data
        valid_users = [user for user in data["results"] if "login" in user and "uuid" in user["login"]]
        if len(valid_users) < len(data["results"]):
            logger.warning(f"{len(data['results']) - len(valid_users)} users had invalid data and were filtered out")
        
        return valid_users
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching random users: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching random users: {str(e)}")
        return []

def generate_random_interests_for_user() -> List[str]:
    """Generate a list of random interests for a user based on a comprehensive list"""
    # Get 3-7 random interests
    import random
    num_interests = random.randint(3, 7)
    return random.sample(ALL_INTERESTS, num_interests)

def generate_personality_traits() -> Dict[str, float]:
    """Generate realistic personality traits for a user (Big Five)"""
    import random
    traits = {}
    for trait in PERSONALITY_TRAITS:
        traits[trait] = round(random.uniform(0.2, 0.9), 2)
    return traits

async def store_random_users_in_neo4j(users: List[Dict[str, Any]]) -> bool:
    """
    Store random users in Neo4j database with enhanced profile data
    """
    from ..db.database import db
    
    existing = db.execute_query("MATCH (u:User) RETURN u.email AS email, u.username AS username")
    existing_emails    = {r["email"]    for r in existing if r.get("email")}
    existing_usernames = {r["username"] for r in existing if r.get("username")}
    start_time = time.time()
    
    try:
        logger.info(f"Preparing to store {len(users)} users in Neo4j...")
        
        # Import database module here to avoid circular imports
        from ..db.database import db
        # Enhanced Cypher query for user batch creation with more attributes
        query = """
        UNWIND $users as user
        MERGE (u:User {id: user.id})
        ON CREATE SET 
            u.email = user.email,
            u.username = user.username,
            u.full_name = user.full_name,
            u.gender = user.gender,
            u.birth_date = user.birth_date,
            u.age = user.age,
            u.location = user.location,
            u.city = user.city,
            u.country = user.country,
            u.latitude = user.latitude,
            u.longitude = user.longitude,
            u.profile_photo = user.profile_photo,
            u.thumbnail_photo = user.thumbnail_photo,
            u.interests = user.interests,
            u.bio = user.bio,
            u.phone = user.phone,
            u.cell = user.cell,
            u.nationality = user.nationality,
            u.trait_openness = user.trait_openness,
            u.trait_conscientiousness = user.trait_conscientiousness,
            u.trait_extroversion = user.trait_extroversion,
            u.trait_agreeableness = user.trait_agreeableness,
            u.trait_neuroticism = user.trait_neuroticism,
            u.created_at = datetime(),
            u.updated_at = datetime(),
            u.is_active = true,
            u.is_verified = true,
            u.login_frequency = user.login_frequency,
            u.profile_updates = user.profile_updates,
            u.reported_count = 0,
            u.suspicious_login_count = 0,
            u.match_score = user.match_score
        """
        
        # Create batches of users to avoid memory issues
        batch_size = 100
        success_count = 0
        failure_count = 0
        total_batches = (len(users) + batch_size - 1) // batch_size  # Ceiling division
        
        logger.info(f"Processing users in {total_batches} batches of {batch_size}")
        
        for batch_num, i in enumerate(range(0, len(users), batch_size), 1):
            batch = users[i:i+batch_size]
            user_batch = []
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} users)...")
            
            for user_index, user in enumerate(batch):
                try:
                    # Generate a random number of login frequency between 1-30 and profile updates between 1-5
                    import random
                    login_frequency = random.randint(1, 30)
                    profile_updates = random.randint(1, 5)
                    
                    # Calculate age from birth date for convenience
                    birth_date = user["dob"]["date"]
                    age = user["dob"]["age"]
                    
                    # Extract relevant user data with enhanced fields
                    user_data = {
                        "id": user["login"]["uuid"],
                        "email": user["email"],
                        "username": user["login"]["username"],
                        "full_name": f"{user['name']['first']} {user['name']['last']}",
                        "gender": user["gender"],
                        "birth_date": birth_date,
                        "age": age,
                        "location": f"{user['location']['city']}, {user['location']['country']}",
                        "city": user['location']['city'],
                        "country": user['location']['country'],
                        "latitude": user['location']['coordinates']['latitude'],
                        "longitude": user['location']['coordinates']['longitude'],
                        "profile_photo": user["picture"]["large"],
                        "thumbnail_photo": user["picture"]["medium"],
                        "interests": generate_random_interests_for_user(),
                        "login_frequency": login_frequency,
                        "profile_updates": profile_updates,
                        "nationality": user["nat"],
                        "phone": user["phone"],
                        "cell": user["cell"],
                        "bio": f"Hi, I'm {user['name']['first']}! I'm from {user['location']['city']} and enjoy meeting new people."
                    }
                    
                    # Get personality traits
                    personality = generate_personality_traits()
                    
                    # Add personality traits as flat properties
                    for trait, value in personality.items():
                        user_data[f"trait_{trait}"] = value
                    
                    # Generate match score based on personality traits (more realistic)
                    match_score = (personality["extroversion"] * 0.3 + 
                                personality["openness"] * 0.3 + 
                                personality["agreeableness"] * 0.2 + 
                                personality["conscientiousness"] * 0.1 + 
                                (1 - personality["neuroticism"]) * 0.1)
                    
                    # Ensure match score is between 0.4 and 0.95
                    match_score = max(0.4, min(0.95, match_score))
                    user_data["match_score"] = round(match_score, 2)
                    
                    user_batch.append(user_data)
                    
                    if user_data["email"] in existing_emails or user_data["username"] in existing_usernames:
                            logger.debug(f"Skipping duplicate user {user_data['email']}/{user_data['username']}")
                            continue

                    # reserve them so we don’t see them again in this run
                    existing_emails.add(user_data["email"])
                    existing_usernames.add(user_data["username"])

                    user_batch.append(user_data)
                    
                    if user_index % 20 == 0 and user_index > 0:
                        logger.debug(f"Processed {user_index}/{len(batch)} users in current batch")
                        
                except KeyError as e:
                    failure_count += 1
                    logger.warning(f"Skipping user due to missing data field: {e}")
                    continue
            
            # Execute batch creation in database
            try:
                logger.info(f"Executing Neo4j query for batch {batch_num} with {len(user_batch)} processed users...")
                
                # Log a sample user for debugging
                if user_batch:
                    logger.debug(f"Sample user data being sent to Neo4j: {user_batch[0]}")
                    
                db.execute_query(query, {"users": user_batch})
                success_count += len(user_batch)
                logger.info(f"Batch {batch_num} stored successfully. Progress: {success_count}/{len(users)} users")
            except Exception as e:
                failure_count += len(user_batch)
                logger.error(f"Error storing batch {batch_num}: {str(e)}")
                logger.error(f"Batch details: {len(user_batch)} users")
                # Log the first error for debugging
                if user_batch:
                    logger.error(f"Sample failed user: {user_batch[0]['id']} - {user_batch[0]['full_name']}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"User ingestion complete. Time elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"Success: {success_count}/{len(users)} users stored in Neo4j")
        logger.info(f"Failures: {failure_count}/{len(users)} users failed to store")
        
        # Create some basic relationships between users to enhance graph structure (optional)
        if success_count > 0:
            try:
                logger.info("Creating initial friendship relationships between users...")
                friendship_query = """
                MATCH (u1:User), (u2:User)
                WHERE u1 <> u2 AND rand() < 0.01  // 1% chance for any two users to be connected
                MERGE (u1)-[:KNOWS]->(u2)
                """
                db.execute_query(friendship_query)
                logger.info("Initial relationships created successfully")
            except Exception as e:
                logger.warning(f"Error creating initial relationships: {str(e)}")
        
        return success_count > 0
    except Exception as e:
        logger.error(f"Error storing random users in Neo4j: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
        return False

async def populate_database_with_random_users(count: int = 1000) -> bool:
    """
    Fetch random users and populate the Neo4j database
    
    Args:
        count: Number of users to fetch and store
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Starting database population with {count} random users...")
    
    # Check if database already has users first
    try:
        from ..db.database import db
        user_count_query = "MATCH (u:User) RETURN count(u) as count"
        result = db.execute_query(user_count_query)
        existing_count = result[0]["count"] if result else 0
        
        if existing_count > 20000:
            logger.info(f"Database already contains {existing_count} users.")
            if existing_count >= count:
                logger.info(f"Skipping population as we already have {existing_count} users (target: {count}).")
                return True
            else:
                # Adjust count to reach the target
                count = count - existing_count
                logger.info(f"Will add {count} more users to reach target of {count + existing_count} total users.")
    except Exception as e:
        logger.warning(f"Could not check existing user count: {str(e)}")
    
    # Fetch users from RandomUser API
    users = await fetch_random_users(count)
    
    if not users:
        logger.error("Failed to fetch random users")
        return False
    
    logger.info(f"Successfully fetched {len(users)} users, proceeding to store in Neo4j...")
    
    # Store users in Neo4j
    success = await store_random_users_in_neo4j(users)
    
    if success:
        logger.info("Database population completed successfully")
    else:
        logger.error("Database population failed")
    
    return success

async def store_social_raw_data(user_id: str, source: str, data: Dict[str, Any]) -> bool:
    """
    Store raw social media data in Neo4j with relationship to user
    """
    try:
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Log the operation
        logger.info(f"Storing raw {source} data for user {user_id}")
        
        # Execute Neo4j query to create relationship and RawBlob node
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (u)-[:RAW_INTEREST {source: $source, created_at: datetime()}]->(r:RawBlob {id: $blob_id})
        SET r.data = $json_data, r.updated_at = datetime()
        RETURN r
        """
        
        blob_id = f"{user_id}_{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.execute_query(query, {
            "user_id": user_id,
            "source": source,
            "json_data": json_data,
            "blob_id": blob_id
        })
        
        logger.info(f"Successfully stored raw data for user {user_id} from source {source}")
        return True
    except Exception as e:
        logger.error(f"Error storing social data: {str(e)}")
        return False

async def get_user_raw_interests(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user's raw social media data from Neo4j
    """
    try:
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        query = """
        MATCH (u:User {id: $user_id})-[r:RAW_INTEREST]->(b:RawBlob)
        RETURN b.data as data, r.source as source
        """
        
        result = db.execute_query(query, {"user_id": user_id})
        
        if not result:
            logger.info(f"No raw interest data found for user {user_id}, returning mock data")
            return get_mock_raw_interests()
        
        # Organize results by source
        interests = {}
        for record in result:
            source = record["source"]
            data = json.loads(record["data"])
            interests[source] = data
            
        return interests
    except Exception as e:
        logger.error(f"Error retrieving raw interests: {str(e)}")
        return get_mock_raw_interests()

def get_mock_raw_interests() -> Dict[str, Any]:
    """Return mock social media interests data"""
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
    Store user topic affinities in Neo4j as proper relationships
    """
    try:
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        logger.info(f"Storing {len(topics)} topics for user {user_id}")
        
        # For each topic, create or update HAS_TOPIC relationship
        for topic_name, score in topics.items():
            query = """
            MATCH (u:User {id: $user_id})
            MERGE (t:Topic {name: $topic_name})
            MERGE (u)-[r:HAS_TOPIC]->(t)
            ON CREATE SET r.score = $score, r.created_at = datetime()
            ON MATCH SET r.score = $score, r.updated_at = datetime()
            """
            
            db.execute_query(query, {
                "user_id": user_id,
                "topic_name": topic_name,
                "score": score
            })
        
        logger.info(f"Successfully stored topics for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing user topics: {str(e)}")
        return False

async def get_user_topics(user_id: str) -> Dict[str, float]:
    """
    Retrieve user's topics and scores from Neo4j
    """
    try:
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        query = """
        MATCH (u:User {id: $user_id})-[r:HAS_TOPIC]->(t:Topic)
        RETURN t.name as topic, r.score as score
        ORDER BY r.score DESC
        """
        
        result = db.execute_query(query, {"user_id": user_id})
        
        if not result:
            logger.info(f"No topics found for user {user_id}, returning generated topics")
            return generate_mock_topics()
            
        # Convert result to dictionary
        topics = {}
        for record in result:
            topics[record["topic"]] = record["score"]
            
        return topics
    except Exception as e:
        logger.error(f"Error retrieving user topics: {str(e)}")
        return generate_mock_topics()

def generate_mock_topics() -> Dict[str, float]:
    """Generate mock topic interests with scores"""
    import random
    
    # Potential topics with realistic score ranges
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
    Get personalized match recommendations for a user from Neo4j based on:
    1. Interests overlap
    2. Location proximity
    3. Age compatibility 
    4. Personality traits compatibility
    
    If Neo4j data is not available, falls back to RandomUser API
    """
    try:
        # Import database module here to avoid circular imports
        from ..db.database import db
        
        # Check if user exists in database
        user_query = """
        MATCH (u:User {id: $user_id})
        RETURN u
        """
        
        user_result = db.execute_query(user_query, {"user_id": user_id})
        
        # If user doesn't exist in database, fall back to RandomUser API
        if not user_result:
            logger.warning(f"User {user_id} not found in database, falling back to RandomUser API")
            return await get_random_recommendations(limit)
        
        # Get the user's data
        user_data = user_result[0]["u"]
        
        # Advanced Neo4j query to find compatible matches based on multiple factors
        match_query = """
        MATCH (u:User {id: $user_id}), (other:User)
        WHERE other.id <> $user_id
        WITH u, other,
             // Calculate interest similarity (Jaccard coefficient)
             size([x IN u.interests WHERE x IN other.interests]) / 
             size(u.interests + [x IN other.interests WHERE NOT x IN u.interests]) AS interest_similarity,
             // Age compatibility (based on typical dating range)
             CASE 
                WHEN abs(u.age - other.age) <= 5 THEN 1.0
                WHEN abs(u.age - other.age) <= 10 THEN 0.8
                WHEN abs(u.age - other.age) <= 15 THEN 0.5
                ELSE 0.2
             END AS age_compatibility
        
        // Calculate an overall match score
        WITH u, other, interest_similarity, age_compatibility,
             (interest_similarity * 0.6 + age_compatibility * 0.4) AS match_score
        
        // Order by match score and limit results
        ORDER BY match_score DESC
        LIMIT $limit
        
        RETURN other {
            .id, .email, .username, .full_name, .gender, .birth_date, .age,
            .location, .city, .country, .profile_photo, .interests, .bio
        } as user_data,
        match_score,
        [x IN other.interests WHERE x IN u.interests] AS common_interests
        """
        
        match_result = db.execute_query(match_query, {"user_id": user_id, "limit": limit})
        
        # If no matches found in database, fall back to RandomUser API
        if not match_result:
            logger.warning(f"No matches found for user {user_id}, falling back to RandomUser API")
            return await get_random_recommendations(limit)
        
        # Format the results
        recommendations = []
        for record in match_result:
            user_data = record["user_data"]
            common_interests = record["common_interests"]
            match_score = record["match_score"]
            
            recommendations.append({
                "id": user_data["id"],
                "full_name": user_data["full_name"],
                "bio": user_data["bio"],
                "interests": user_data["interests"],
                "location": user_data["location"],
                "birth_date": user_data["birth_date"],
                "profile_photo": user_data["profile_photo"],
                "match_score": match_score,
                "common_topics": common_interests
            })
        
        logger.info(f"Found {len(recommendations)} recommendations for user {user_id} from Neo4j")
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        logger.info("Falling back to RandomUser API for recommendations")
        return await get_random_recommendations(limit)

async def get_random_recommendations(limit: int = 10) -> List[Dict[str, Any]]:
    """Get random recommendations using RandomUser API as fallback"""
    # Fetch random users for recommendations
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
            "match_score": _lat_to_match_score(user["location"]["coordinates"]["latitude"]),
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


import random        #  ← new, if not already present

def _lat_to_match_score(lat_str: str) -> float:
    """
    Convert a latitude string (e.g. '44.9877', '-65.2995') into a
    deterministic-but-arbitrary match-score in the range 0.40 – 0.95.
    Never raises.
    """
    try:
        score = abs(float(lat_str)) % 100 / 100.0   # 0-1
        score = round(score, 2)
    except (ValueError, TypeError):
        score = round(random.uniform(0.4, 0.95), 2)
    return min(0.95, max(0.40, score))