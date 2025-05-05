from typing import List, Dict, Any

import requests

from backend.db.neo4j_client import RANDOM_USER_API
from ..models.user import UserInDB, UserPreferences
from ..db.database import db
from .ml_integration import ml_service
import numpy as np
from datetime import datetime, timedelta
import os
import random

def calculate_age(birth_date: datetime) -> int:
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

def calculate_interest_similarity(user_interests: List[str], candidate_interests: List[str]) -> float:
    if not user_interests or not candidate_interests:
        return 0.0
    
    # Convert interests to sets for easier comparison
    user_set = set(user_interests)
    candidate_set = set(candidate_interests)
    
    # Calculate Jaccard similarity
    intersection = len(user_set.intersection(candidate_set))
    union = len(user_set.union(candidate_set))
    
    return intersection / union if union > 0 else 0.0

def get_matches(user: UserInDB, preferences: UserPreferences, limit: int = 10) -> List[Dict[str, Any]]:
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        # Generate mock matches data
        return generate_mock_matches(limit)
        
    user_age = calculate_age(user.birth_date)
    
    # Build the Cypher query based on preferences
    query = """
    MATCH (u:User)
    WHERE u.email <> $email
    AND u.is_active = true
    """
    
    params = {"email": user.email}
    
    # Add gender preference filter if specified
    if preferences.preferred_gender:
        query += "AND u.gender IN $preferred_gender "
        params["preferred_gender"] = [g.value for g in preferences.preferred_gender]
    
    # Add age range filter
    query += """
    AND datetime(u.birth_date).year <= datetime().year - $min_age
    AND datetime(u.birth_date).year >= datetime().year - $max_age
    """
    params.update({
        "min_age": preferences.min_age,
        "max_age": preferences.max_age
    })
    
    # Get potential matches
    query += """
    WITH u,
         count { (u)-[:MATCHED]->() } as matches_count,
         count { (u)-[:SENT]->() } as message_count,
         avg(size((u)-[:SENT]->().content)) as avg_message_length
    RETURN {
        id: u.id,
        email: u.email,
        username: u.username,
        full_name: u.full_name,
        gender: u.gender,
        birth_date: u.birth_date,
        bio: u.bio,
        interests: u.interests,
        location: u.location,
        profile_photo: u.profile_photo,
        matches_count: matches_count,
        message_count: message_count,
        avg_message_length: avg_message_length,
        login_frequency: u.login_frequency,
        profile_updates: u.profile_updates,
        reported_count: coalesce(u.reported_count, 0),
        suspicious_login_count: coalesce(u.suspicious_login_count, 0)
    } as user_data
    """
    
    results = db.execute_query(query, params)
    
    if not results:
        return []
    
    candidates = [result["user_data"] for result in results]
    
    # Use enhanced ML-based matching
    matches = ml_service.get_enhanced_matches(user, preferences, candidates)
    
    if not matches:
        # Fallback to basic matching if ML service fails
        matches = []
        for candidate in candidates:
            # Calculate basic match score
            interest_similarity = calculate_interest_similarity(
                user.interests,
                candidate.get("interests", [])
            )
            
            matches.append({
                **candidate,
                "match_score": round(interest_similarity * 100, 2)
            })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matches[:limit]

def generate_mock_matches(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate `count` mock matches by fetching real-looking users from RandomUser.me,
    including their email, and blending in a pseudo match_score.
    """
    # 1. Fetch real user profiles including email
    resp = requests.get(
        RANDOM_USER_API,
        params={
            "results": count,
            "nat": "us,gb,ca,au",
            "inc": "gender,name,location,login,dob,picture,email"
        }
    )
    resp.raise_for_status()
    raw_users = resp.json().get("results", [])

    matches: List[Dict[str, Any]] = []
    for u in raw_users:
        first = u["name"]["first"]
        last  = u["name"]["last"]
        city  = u["location"]["city"]
        country = u["location"]["country"]

        # 2. Build the candidate dict safely, using get() for email
        candidate: Dict[str, Any] = {
            "id": u["login"]["uuid"],
            "email": u.get("email", ""),                       # safe access
            "username": u["login"]["username"],
            "full_name": f"{first} {last}",
            "gender": u["gender"],
            "birth_date": u["dob"]["date"],
            "bio": f"Hey, I'm {first} from {city}! 👋",
            "interests": random.sample(
                ["Travel","Photography","Cooking","Fitness","Reading",
                 "Art","Music","Movies","Gaming","Technology"],
                k=random.randint(2,5)
            ),
            "location": f"{city}, {country}",
            "profile_photo": u["picture"]["large"],
        }

        # 3. Derive a pseudo-random match_score in [0.4, 0.95]
        lat = float(u["location"]["coordinates"]["latitude"])
        raw_score = abs(int(lat)) % 100 / 100.0
        score = min(max(raw_score, 0.4), 0.95)
        candidate["match_score"] = round(score, 2)

        matches.append(candidate)

    # 4. Sort by match_score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches

def create_match(user_id: str, matched_user_id: str, match_score: float) -> Dict[str, Any]:
    """
    Create a match between two users with 'pending' status
    
    Args:
        user_id: ID of the user who likes the other user
        matched_user_id: ID of the user being liked
        match_score: Match score between the two users
        
    Returns:
        The created match relationship
    """
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        # Return mock match data
        return {
            "score": match_score,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
    query = """
    MATCH (u1:User {id: $user_id}), (u2:User {id: $matched_user_id})
    CREATE (u1)-[r:MATCHED {
        score: $match_score,
        created_at: datetime(),
        status: 'pending'
    }]->(u2)
    RETURN r
    """
    
    try:
        result = db.execute_query(
            query,
            {
                "user_id": user_id,
                "matched_user_id": matched_user_id,
                "match_score": match_score
            }
        )
        
        # Check if there is a mutual match (other user has already liked this user)
        mutual_query = """
        MATCH (u1:User {id: $user_id})<-[r:MATCHED]-(u2:User {id: $matched_user_id})
        WHERE r.status = 'pending'
        RETURN r
        """
        
        mutual_result = db.execute_query(
            mutual_query,
            {
                "user_id": user_id,
                "matched_user_id": matched_user_id
            }
        )
        
        # If there is a mutual match, update both relationships to 'accepted'
        if mutual_result:
            update_query = """
            MATCH (u1:User {id: $user_id})-[r1:MATCHED]->(u2:User {id: $matched_user_id}),
                  (u1)<-[r2:MATCHED]-(u2)
            SET r1.status = 'accepted', r1.accepted_at = datetime(),
                r2.status = 'accepted', r2.accepted_at = datetime()
            """
            
            db.execute_query(
                update_query,
                {
                    "user_id": user_id,
                    "matched_user_id": matched_user_id
                }
            )
            
        return result[0]["r"]
    except Exception as e:
        print(f"Error creating match: {e}")
        if superadmin_mode:
            return {
                "score": match_score,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
        return {}

def accept_match(user_id: str, matched_user_id: str) -> Dict[str, Any]:
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        # Return mock match data
        return {
            "status": "accepted",
            "accepted_at": datetime.now().isoformat()
        }
        
    query = """
    MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User {id: $matched_user_id})
    SET r.status = 'accepted', r.accepted_at = datetime()
    RETURN r
    """
    
    result = db.execute_query(
        query,
        {
            "user_id": user_id,
            "matched_user_id": matched_user_id
        }
    )
    return result[0]["r"]

def reject_match(user_id: str, matched_user_id: str) -> Dict[str, Any]:
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        # Return mock match data
        return {
            "status": "rejected",
            "rejected_at": datetime.now().isoformat()
        }
        
    query = """
    MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User {id: $matched_user_id})
    SET r.status = 'rejected', r.rejected_at = datetime()
    RETURN r
    """
    
    result = db.execute_query(
        query,
        {
            "user_id": user_id,
            "matched_user_id": matched_user_id
        }
    )
    return result[0]["r"] 