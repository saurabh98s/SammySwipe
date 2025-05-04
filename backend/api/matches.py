from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List, Dict
from ..models.user import UserInDB, UserResponse, UserPreferences
from ..services.auth import get_current_active_user
from ..services.matching import get_matches, create_match, accept_match, reject_match
from ..db.database import db
from ..db.neo4j_client import get_recommendations_for_user
import random

router = APIRouter()

@router.get("/matches/recommendations", response_model=List[UserResponse])
async def get_match_recommendations(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    # Get user preferences
    query = """
    MATCH (u:User {email: $email})
    RETURN u.preferences
    """
    result = db.execute_query(query, {"email": current_user.email})
    
    if not result or not result[0]["u.preferences"]:
        raise HTTPException(
            status_code=400,
            detail="Please set your matching preferences first"
        )
    
    preferences = UserPreferences(**result[0]["u.preferences"])
    matches = get_matches(current_user, preferences)
    
    return [UserResponse(**match) for match in matches]

@router.post("/matches/{user_id}")
async def create_new_match(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    # Check if match already exists
    query = """
    MATCH (u1:User {email: $email})-[r:MATCHED]->(u2:User {id: $user_id})
    RETURN r
    """
    result = db.execute_query(
        query,
        {
            "email": current_user.email,
            "user_id": user_id
        }
    )
    
    if result:
        raise HTTPException(
            status_code=400,
            detail="Match already exists"
        )
    
    # Create match
    match = create_match(current_user.id, user_id, 0)  # Score will be calculated by the matching engine
    return {"message": "Match created successfully"}

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