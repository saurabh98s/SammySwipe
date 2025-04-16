from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from ..models.user import UserInDB, UserResponse, UserPreferences
from ..services.auth import get_current_active_user
from ..services.matching import get_matches, create_match, accept_match, reject_match
from ..db.database import db

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