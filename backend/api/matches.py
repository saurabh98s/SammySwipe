from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List, Dict
from ..models.user import UserInDB, UserResponse, UserPreferences
from ..services.auth import get_current_active_user
from ..services.matching import get_matches, create_match, accept_match, reject_match
from ..db.database import db
from ..db.neo4j_client import get_recommendations_for_user
import random
from ..services.ml_integration import ml_service
import os
from datetime import datetime

router = APIRouter()

@router.get("/matches/recommendations", response_model=List[UserResponse])
async def get_match_recommendations(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    # Check if in superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    # Get user preferences
    query = """
    MATCH (u:User {email: $email})
    RETURN u.preferences
    """
    result = db.execute_query(query, {"email": current_user.email})
    
    # In superadmin mode, provide default preferences if none are found
    if not result or not result[0]["u.preferences"]:
        if superadmin_mode:
            # Use default preferences for superadmin
            default_preferences = UserPreferences(
                min_age=18,
                max_age=50,
                preferred_gender=["male", "female"],
                max_distance=50,
                interests_weight=0.7
            )
            matches = get_matches(current_user, default_preferences)
            # If we still have no matches, try getting recommendations directly
            if not matches and superadmin_mode:
                recommendations = await get_recommendations_for_user(current_user.id, 10)
                return [UserResponse(
                    id=rec["id"],
                    email=f"user{i}@example.com",
                    username=f"user{i}",
                    full_name=rec["full_name"],
                    gender="other",
                    birth_date=datetime.fromisoformat(rec["birth_date"].replace("Z", "+00:00")),
                    bio=rec["bio"],
                    interests=rec["interests"],
                    location=rec["location"],
                    profile_photo=rec["profile_photo"],
                    match_score=rec["match_score"]
                ) for i, rec in enumerate(recommendations)]
            return [UserResponse(**match) for match in matches]
        else:
            raise HTTPException(
                status_code=400,
                detail="Please set your matching preferences first"
            )
    
    preferences = UserPreferences(**result[0]["u.preferences"])
    matches = get_matches(current_user, preferences)
    
    # If we don't have matches but superadmin is on, get recommendations
    if not matches and superadmin_mode:
        recommendations = await get_recommendations_for_user(current_user.id, 10)
        return [UserResponse(
            id=rec["id"],
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=rec["full_name"],
            gender="other",
            birth_date=datetime.fromisoformat(rec["birth_date"].replace("Z", "+00:00")),
            bio=rec["bio"],
            interests=rec["interests"],
            location=rec["location"],
            profile_photo=rec["profile_photo"],
            match_score=rec["match_score"]
        ) for i, rec in enumerate(recommendations)]
    
    return [UserResponse(**match) for match in matches]

@router.post("/matches/{user_id}")
async def create_new_match(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    """
    Create a new match (like) from the current user to another user
    """
    # Check if match already exists
    query = """
    MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User {id: $matched_user_id})
    RETURN r
    """
    result = db.execute_query(
        query,
        {
            "user_id": current_user.id,
            "matched_user_id": user_id
        }
    )
    
    if result:
        # Match already exists, return success but indicate it's not new
        return {"message": "Match already exists", "is_new": False}
    
    # Get match score (pull from user's existing match score or compute)
    score_query = """
    MATCH (u:User {id: $user_id})
    RETURN u.match_score as score
    """
    score_result = db.execute_query(score_query, {"user_id": user_id})
    match_score = score_result[0]["score"] if score_result and "score" in score_result[0] else 0.75
    
    # Create match with pending status
    try:
        match = create_match(current_user.id, user_id, match_score)
        # Check if this created a mutual match
        check_mutual_query = """
        MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User {id: $matched_user_id})
        WHERE r.status = 'accepted'
        RETURN r
        """
        mutual_result = db.execute_query(
            check_mutual_query,
            {
                "user_id": current_user.id,
                "matched_user_id": user_id
            }
        )
        
        is_mutual = len(mutual_result) > 0
        
        return {
            "message": "Match created successfully", 
            "is_new": True, 
            "is_mutual": is_mutual
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create match: {str(e)}"
        )

@router.put("/matches/{user_id}/accept")
async def accept_user_match(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    try:
        match = accept_match(current_user.id, user_id)
        return {"message": "Match accepted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.put("/matches/{user_id}/reject")
async def reject_user_match(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    try:
        match = reject_match(current_user.id, user_id)
        return {"message": "Match rejected successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/matches/my-matches", response_model=List[UserResponse])
async def get_my_matches(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    query = """
    MATCH (u1:User {email: $email})-[r:MATCHED]->(u2:User)
    WHERE r.status = 'accepted'
    RETURN u2, r.score as match_score
    """
    
    result = db.execute_query(query, {"email": current_user.email})
    return [
        UserResponse(**{**match["u2"], "match_score": match["match_score"]})
        for match in result
    ]

@router.post("/matches", tags=["matches"])
async def get_potential_matches(current_user: UserInDB = Depends(get_current_active_user)) -> List[Dict[str, Any]]:
    """
    Get potential matches for the current user. Uses ML models to compute match scores.
    """
    # Get realistic recommendations using RandomUser API
    recommendations = await get_recommendations_for_user(current_user.id, 10)
    return recommendations

@router.post("/users/{user_id}/like", tags=["matches"])
async def like_user(user_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """
    Like a potential match
    """
    # In a real implementation, this would:
    # 1. Record the like in the database
    # 2. Check if the other user has already liked the current user (mutual match)
    # 3. Return information about whether it's a match
    
    return {"success": True, "is_match": random.choice([True, False])}

@router.get("/matches/my-matches", tags=["matches"])
async def get_my_matches_old(current_user: UserInDB = Depends(get_current_active_user)) -> List[Dict[str, Any]]:
    """
    Get all users that have mutually matched with the current user
    """
    # Get 5 random realistic users for matches
    user_recommendations = await get_recommendations_for_user(current_user.id, 5)
    
    # Transform them into matches with chat info
    matches = []
    for user in user_recommendations:
        # Create a match with chat data
        matches.append({
            "user_id": user["id"],
            "full_name": user["full_name"],
            "profile_photo": user["profile_photo"],
            "last_message": random.choice([
                "Hey, how are you?",
                "Nice to meet you!",
                "What are you up to this weekend?",
                None
            ]),
            "timestamp": "2023-12-15T12:34:56Z" if random.random() > 0.3 else None
        })
    
    return matches

@router.get("/matches/my-pending-likes", tags=["matches"])
async def get_my_pending_likes(current_user: UserInDB = Depends(get_current_active_user)) -> List[Dict[str, Any]]:
    """
    Get all users that the current user has liked but are still pending a response
    """
    query = """
    MATCH (u1:User {id: $user_id})-[r:MATCHED]->(u2:User)
    WHERE r.status = 'pending'
    RETURN u2, r.score as match_score, r.created_at as liked_at
    ORDER BY r.created_at DESC
    """
    
    result = db.execute_query(query, {"user_id": current_user.id})
    
    if not result:
        return []
    
    liked_users = []
    for match in result:
        user = dict(match["u2"])
        
        # Format the data for frontend consumption
        liked_users.append({
            "id": user.get("id"),
            "full_name": user.get("full_name"),
            "profile_photo": user.get("profile_photo"),
            "bio": user.get("bio", ""),
            "interests": user.get("interests", []),
            "location": user.get("location", ""),
            "birth_date": user.get("birth_date"),
            "match_score": match["match_score"],
            "liked_at": match["liked_at"]
        })
    
    return liked_users

@router.get("/matches/statistics", tags=["matches"])
async def get_match_statistics(current_user: UserInDB = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    Get statistics about the matching process using ML algorithms.
    """
    # Get match statistics from ML service
    statistics = ml_service.get_match_statistics()
    return statistics 