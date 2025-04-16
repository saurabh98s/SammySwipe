from typing import List, Dict, Any
from ..models.user import UserInDB, UserPreferences
from ..db.database import db
from .ml_integration import ml_service
import numpy as np
from datetime import datetime

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

def create_match(user_id: str, matched_user_id: str, match_score: float) -> Dict[str, Any]:
    query = """
    MATCH (u1:User {id: $user_id}), (u2:User {id: $matched_user_id})
    CREATE (u1)-[r:MATCHED {
        score: $match_score,
        created_at: datetime(),
        status: 'pending'
    }]->(u2)
    RETURN r
    """
    
    result = db.execute_query(
        query,
        {
            "user_id": user_id,
            "matched_user_id": matched_user_id,
            "match_score": match_score
        }
    )
    return result[0]["r"]

def accept_match(user_id: str, matched_user_id: str) -> Dict[str, Any]:
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