from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Any, List
from ..models.user import UserUpdate, UserResponse, UserInDB, UserPreferences
from ..services.auth import get_current_active_user
from ..db.database import db
import base64

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
async def read_user_me(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    query = """
    MATCH (u:User {email: $email})
    SET u += $updates, u.updated_at = datetime()
    RETURN u
    """
    
    updates = {k: v for k, v in user_in.dict(exclude_unset=True).items()}
    if not updates:
        return current_user
        
    result = db.execute_query(
        query,
        {
            "email": current_user.email,
            "updates": updates
        }
    )
    return UserResponse(**result[0]["u"])

@router.post("/users/me/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    contents = await file.read()
    base64_image = base64.b64encode(contents).decode()
    
    query = """
    MATCH (u:User {email: $email})
    SET u.profile_photo = $photo, u.updated_at = datetime()
    RETURN u
    """
    
    result = db.execute_query(
        query,
        {
            "email": current_user.email,
            "photo": f"data:{file.content_type};base64,{base64_image}"
        }
    )
    return {"message": "Profile photo updated successfully"}

@router.put("/users/me/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    query = """
    MATCH (u:User {email: $email})
    SET u.preferences = $preferences, u.updated_at = datetime()
    RETURN u
    """
    
    result = db.execute_query(
        query,
        {
            "email": current_user.email,
            "preferences": preferences.dict()
        }
    )
    return {"message": "Preferences updated successfully"}

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    query = """
    MATCH (u:User {id: $user_id})
    RETURN u
    """
    
    result = db.execute_query(query, {"user_id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(**result[0]["u"]) 