from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from ..core.config import get_settings
from ..models.user import UserCreate, Token, UserResponse
from ..services.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from ..services.ml_integration import ml_service
from ..db.database import db
from ..db.neo4j_client import store_social_raw_data
from typing import Any, Dict
import uuid
import os
import jwt
from jwt.exceptions import PyJWTError
# from ..services.social_api import social_api_service

settings = get_settings()
router = APIRouter(tags=["auth"])

@router.post("/auth/register", response_model=UserResponse)
async def register(user_in: UserCreate) -> Any:
    # Check if user exists
    query = """
    MATCH (u:User {email: $email}) RETURN u
    """
    result = db.execute_query(query, {"email": user_in.email})
    if result:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Check for potential fraud
    user_data = user_in.dict()
    if ml_service.check_fraud(user_data):
        raise HTTPException(
            status_code=400,
            detail="Registration blocked due to suspicious activity"
        )
    
    # Create user
    hashed_password = get_password_hash(user_in.password)
    query = """
    CREATE (u:User {
        email: $email,
        username: $username,
        full_name: $full_name,
        hashed_password: $hashed_password,
        gender: $gender,
        birth_date: $birth_date,
        bio: $bio,
        interests: $interests,
        location: $location,
        profile_photo: $profile_photo,
        created_at: datetime(),
        updated_at: datetime(),
        is_active: true,
        is_verified: false,
        login_frequency: 0,
        profile_updates: 0,
        reported_count: 0,
        suspicious_login_count: 0
    })
    RETURN u
    """
    
    user_data = user_in.dict()
    user_data["hashed_password"] = hashed_password
    
    result = db.execute_query(query, user_data)
    
    # Analyze user metadata
    metadata = ml_service.analyze_user(user_data)
    
    # Update user with metadata
    if metadata:
        update_query = """
        MATCH (u:User {email: $email})
        SET u.metadata = $metadata
        """
        db.execute_query(
            update_query,
            {
                "email": user_data["email"],
                "metadata": metadata
            }
        )
    
    return UserResponse(**result[0]["u"])

@router.post("/auth/register_test", response_model=UserResponse)
async def register_test(user_in: UserCreate) -> Any:
    # Check if user exists
    query = """
    MATCH (u:User {email: $email}) RETURN u
    """
    result = db.execute_query(query, {"email": user_in.email})
    if result:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Create user without fraud check
    hashed_password = get_password_hash(user_in.password)
    user_id = str(uuid.uuid4())
    query = """
    CREATE (u:User {
        id: $id,
        email: $email,
        username: $username,
        full_name: $full_name,
        hashed_password: $hashed_password,
        gender: $gender,
        birth_date: $birth_date,
        bio: $bio,
        interests: $interests,
        location: $location,
        profile_photo: $profile_photo,
        created_at: datetime(),
        updated_at: datetime(),
        is_active: true,
        is_verified: false,
        login_frequency: 0,
        profile_updates: 0,
        reported_count: 0,
        suspicious_login_count: 0
    })
    RETURN u
    """
    
    user_data = user_in.dict()
    user_data["hashed_password"] = hashed_password
    user_data["id"] = user_id
    result = db.execute_query(query, user_data)
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Could not create user"
        )
    
    # Convert Neo4j DateTime to Python datetime
    user_dict = dict(result[0]["u"])
    if "birth_date" in user_dict:
        # Handle Neo4j DateTime conversion
        birth_date_str = str(user_dict["birth_date"])
        # Remove any extra precision in microseconds
        if "." in birth_date_str:
            parts = birth_date_str.split(".")
            if len(parts) > 1:
                # Keep only 6 digits for microseconds
                micros = parts[1][:6]
                birth_date_str = f"{parts[0]}.{micros}{parts[1][-6:]}"
        
        # Ensure proper timezone format
        if "Z" in birth_date_str:
            birth_date_str = birth_date_str.replace("Z", "+00:00")
        
        user_dict["birth_date"] = datetime.fromisoformat(birth_date_str)
        
    return UserResponse(**user_dict)

@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    """
    result = db.execute_query(query, {"email": form_data.username})
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = result[0]["u"]
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Update login frequency
    update_query = """
    MATCH (u:User {email: $email})
    SET u.login_frequency = coalesce(u.login_frequency, 0) + 1,
        u.last_login = datetime()
    """
    db.execute_query(update_query, {"email": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Social Media OAuth endpoints

# @router.get("/twitter")
# async def twitter_auth_redirect():
#     """Redirect to Twitter OAuth"""
#     redirect_url = await social_api_service.twitter_oauth_redirect()
#     return {"redirect_url": redirect_url}

# @router.get("/twitter/callback")
# async def twitter_auth_callback(code: str = Query(...), state: str = Query(...)):
#     """Handle Twitter OAuth callback"""
#     # Verify state parameter to prevent CSRF attacks (not implemented in this demo)
    
#     # Exchange code for token
#     token_data = await social_api_service.twitter_oauth_callback(code)
    
#     # Fetch user data from Twitter
#     user_data = await social_api_service.twitter_fetch_user_data(token_data["access_token"])
    
#     # Store raw data in Neo4j
#     # In a real implementation, this would be linked to the user account
#     user_id = "current_user_id"  # This would be the actual user ID
#     await store_social_raw_data(user_id, "twitter", user_data)
    
#     # Return success response with option to redirect
#     return {
#         "success": True, 
#         "message": "Twitter account connected successfully",
#         "redirect_url": "/dashboard/profile"
#     }

# @router.get("/facebook")
# async def facebook_auth_redirect():
#     """Redirect to Facebook OAuth"""
#     redirect_url = await social_api_service.facebook_oauth_redirect()
#     return {"redirect_url": redirect_url}

# @router.get("/facebook/callback")
# async def facebook_auth_callback(code: str = Query(...), state: str = Query(...)):
#     """Handle Facebook OAuth callback"""
#     # Verify state parameter to prevent CSRF attacks (not implemented in this demo)
    
#     # Exchange code for token
#     token_data = await social_api_service.facebook_oauth_callback(code)
    
#     # Fetch user data from Facebook
#     user_data = await social_api_service.facebook_fetch_user_data(token_data["access_token"])
    
#     # Store raw data in Neo4j
#     # In a real implementation, this would be linked to the user account
#     user_id = "current_user_id"  # This would be the actual user ID
#     await store_social_raw_data(user_id, "facebook", user_data)
    
#     # Return success response with option to redirect
#     return {
#         "success": True, 
#         "message": "Facebook account connected successfully",
#         "redirect_url": "/dashboard/profile"
#     }

# @router.get("/instagram")
# async def instagram_auth_redirect():
#     """Redirect to Instagram OAuth"""
#     redirect_url = await social_api_service.instagram_oauth_redirect()
#     return {"redirect_url": redirect_url}

# @router.get("/instagram/callback")
# async def instagram_auth_callback(code: str = Query(...), state: str = Query(...)):
#     """Handle Instagram OAuth callback"""
#     # Verify state parameter to prevent CSRF attacks (not implemented in this demo)
    
#     # Exchange code for token
#     token_data = await social_api_service.instagram_oauth_callback(code)
    
#     # Fetch user data from Instagram
#     user_data = await social_api_service.instagram_fetch_user_data(token_data["access_token"])
    
#     # Store raw data in Neo4j
#     # In a real implementation, this would be linked to the user account
#     user_id = "current_user_id"  # This would be the actual user ID
#     await store_social_raw_data(user_id, "instagram", user_data)
    
#     # Return success response with option to redirect
#     return {
#         "success": True, 
#         "message": "Instagram account connected successfully",
#         "redirect_url": "/dashboard/profile"
#     } 