from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from typing import Any, List, Dict, Optional
from ..models.user import UserUpdate, UserResponse, UserInDB, UserPreferences
from ..services.auth import get_current_active_user, get_current_user
from ..db.database import db
from ..db.neo4j_client import get_user_raw_interests, store_user_topics
import base64
from pydantic import BaseModel
from starlette.requests import Request          # keep this import

# Mock the ML pipeline imports
class SocialDataPreprocessor:
    def extract_text_from_raw_data(self, raw_data):
        # Mock implementation
        all_text = []
        # Extract from Twitter
        if 'twitter' in raw_data and 'tweets' in raw_data['twitter']:
            for tweet in raw_data['twitter']['tweets']:
                if 'text' in tweet:
                    all_text.append(tweet['text'])
        
        # Extract from Instagram
        if 'instagram' in raw_data and 'media' in raw_data['instagram'] and 'data' in raw_data['instagram']['media']:
            for post in raw_data['instagram']['media']['data']:
                if 'caption' in post:
                    all_text.append(post['caption'])
        
        # Extract from Facebook
        if 'facebook' in raw_data and 'posts' in raw_data['facebook'] and 'data' in raw_data['facebook']['posts']:
            for post in raw_data['facebook']['posts']['data']:
                if 'message' in post:
                    all_text.append(post['message'])
        
        return " ".join(all_text)

class InterestAnalyzer:
    def analyze_interests(self, text):
        # Mock implementation - generate random topics
        import random
        
        topics = {
            "Travel": round(random.uniform(0.7, 0.95), 2),
            "Technology": round(random.uniform(0.65, 0.9), 2),
            "Food": round(random.uniform(0.5, 0.85), 2),
            "Fashion": round(random.uniform(0.4, 0.75), 2),
            "Sports": round(random.uniform(0.3, 0.8), 2),
            "Music": round(random.uniform(0.55, 0.9), 2),
            "Movies": round(random.uniform(0.45, 0.85), 2),
            "Art": round(random.uniform(0.4, 0.8), 2)
        }
        
        # Sort by score descending
        return dict(sorted(topics.items(), key=lambda item: item[1], reverse=True))

router = APIRouter()

class SocialHandles(BaseModel):
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    social_handles: Optional[SocialHandles] = None

@router.get("/users/me", response_model=UserResponse)
async def get_me(
    current_user: UserInDB = Depends(get_current_user),
):
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

@router.get("/me", tags=["users"])
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_active_user)) -> Dict[str, Any]:
    """
    Get the current user's profile
    """
    # In a real implementation, this would return the user from the database
    # For now, we'll return the user from the token with some additional fields
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": getattr(current_user, "full_name", "User Name"),
        "gender": getattr(current_user, "gender", "unspecified"),
        "birth_date": getattr(current_user, "birth_date", "1990-01-01"),
        "bio": getattr(current_user, "bio", "No bio yet"),
        "profile_photo": getattr(current_user, "profile_photo", None),
        "interests": getattr(current_user, "interests", []),
        "location": getattr(current_user, "location", None),
        "twitter_handle": getattr(current_user, "twitter_handle", None),
        "instagram_handle": getattr(current_user, "instagram_handle", None),
        "facebook_handle": getattr(current_user, "facebook_handle", None),
    }

@router.put("/me", tags=["users"])
async def update_profile(
    profile_data: UpdateProfileRequest, 
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Update the current user's profile
    """
    # In a real implementation, this would update the user in the database
    # For demonstration, we'll just echo back the updated data
    
    updated_user = get_current_user_profile(current_user)
    
    if profile_data.full_name:
        updated_user["full_name"] = profile_data.full_name
    
    if profile_data.bio:
        updated_user["bio"] = profile_data.bio
    
    if profile_data.profile_photo:
        updated_user["profile_photo"] = profile_data.profile_photo
    
    if profile_data.social_handles:
        if profile_data.social_handles.twitter:
            updated_user["twitter_handle"] = profile_data.social_handles.twitter
        
        if profile_data.social_handles.instagram:
            updated_user["instagram_handle"] = profile_data.social_handles.instagram
        
        if profile_data.social_handles.facebook:
            updated_user["facebook_handle"] = profile_data.social_handles.facebook
    
    return updated_user 

@router.post("/analyze-interests/{user_id}", tags=["users"])
async def analyze_user_interests(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Analyze user interests based on their social media data
    """
    # Check if the user has permission to analyze this user's interests
    if user_id != "me" and user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only analyze your own interests"
        )
    
    user_id = current_user.id  # Use the actual user ID
    
    # Get raw social media data
    raw_data = await get_user_raw_interests(user_id)
    
    # Initialize the preprocessor
    preprocessor = SocialDataPreprocessor()
    
    # Extract and preprocess text
    processed_text = preprocessor.extract_text_from_raw_data(raw_data)
    
    # If no text was found, return an error
    if not processed_text:
        return {
            "success": False,
            "message": "No social media data found. Please connect at least one social media account.",
            "topics": {}
        }
    
    # Initialize the interest analyzer
    analyzer = InterestAnalyzer()
    
    # Analyze interests
    topics = analyzer.analyze_interests(processed_text)
    
    # Store the topics in Neo4j
    await store_user_topics(user_id, topics)
    
    return {
        "success": True,
        "message": "Interests analyzed successfully",
        "topics": topics
    } 